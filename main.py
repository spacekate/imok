#!/usr/bin/env python
#
# I'm OK! website

import cgi
import os
import re
import wsgiref.handlers
import logging
import mimetypes
import urllib
import demjson
import logging

from datetime import datetime
from html2text import html2text

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import urlfetch
from google.appengine.api import mail

from models import *
from constants import *

### Base Classes
class ReqHandler(webapp.RequestHandler):
    def getAccount(self):
        if (not users.get_current_user()):
            return None
        accountQuery = Customer.gql("WHERE account = :1 LIMIT 1",
                               users.get_current_user())
        
        account = accountQuery.get()
        if (not account):
            customer = Customer()
            customer.account = users.get_current_user()
            customer.name = customer.account.nickname()
            customer.email = customer.account.email()
            customer.timeout=24*60   #24 hours * 60 mins
            customer.phone=''
            customer.mobile=''
            customer.comment=''
            customer.notify()
            customer.put()
            account=customer
        return account
    def getJsonContacts(self, message=''):
        account = self.getAccount()
        contacts = []
        for contact in account.contact_set:
            contacts.append( {'email': contact.email, 'key': str(contact.key()), 'status': contact.status })
        result = {'contacts': contacts}
        result['message'] = message
        return(demjson.encode(result))
        
    def template(self, templateName, values):
        self.response.out.write(self.getTemplate(templateName, values))

    def getTemplate(self, templateName, values):
        if (users.get_current_user()):
            values['logoutLink'] = users.create_logout_url("/")
        if (users.is_current_user_admin()):
            values['isAdmin'] = True
        values['domain'] = Constants().domain()
        path = os.path.join(os.path.dirname(__file__),'templates', templateName)
        return (template.render(path, values))

### Save Handlers
class NotificationHandler(ReqHandler):
    def notify(self, vendorId, deviceId, customer=None):
        if (customer):
            self.notifyCustomer(customer)
        else:
            sourceQuery = Source.gql("WHERE vendorId =:1 and deviceId = :2 ", vendorId, deviceId)
            sourceResults = sourceQuery.fetch(1)
            for source in sourceResults:
                self.notifyCustomer(source.customer)
                customer=source.cutomer
           
        notification = Notification()
        notification.vendorId = vendorId
        notification.deviceId = deviceId
        notification.dateTime=datetime.utcnow()
        notification.customer=customer
        notification.put()

    def notifyCustomer(self, customer):
        customer.notify()
        customer.put()
        alertQuery = Alert.gql("WHERE customer =:1 and closed = :2 LIMIT 1", customer, False)
        alert = alertQuery.get()
        if (alert):
            alert.closed=True
            alert.put()
class WebNotificationHandler(NotificationHandler):
    def get(self):
        customer = self.getAccount()
        self.notify("website", str(customer.key().id()), customer)        
        self.redirect('/account.html')
        
class ExternalNotificationHandler(NotificationHandler):
    def get(self):
        vendorId = self.request.get('vendorId')
        deviceId = self.request.get('deviceId')
        self.notify(vendorId, deviceId)
        
        self.redirect('/account.html')
        
class SaveSettingsHandler(ReqHandler):
    def get(self):
        customer = self.getAccount()
        
        customer.name   = self.request.get('name', customer.name)
        customer.phone  = self.request.get('phone', customer.phone)
        customer.mobile  = self.request.get('mobile', customer.mobile)
        customer.email  = self.request.get('email', customer.email)
        customer.timeout= int(self.request.get('timeout', customer.timeout))
        customer.comment = self.request.get('comment', customer.comment)

        customer.put()
        self.redirect('/settings.html')

        
class NewContactHandler(ReqHandler):
    def get(self):
        contact = Contact()
        contact.customer=self.getAccount()
        contact.email=self.request.get('newContact')
        contact.status='pending'
        message=self.verifyContact(contact)
        if (not message):
            contact.put()
            self.sendVerificationMessage(contact)
        self.response.out.write(self.getJsonContacts(message))
        
    def verifyContact(self, contact):
        contactQuery = Contact.gql("WHERE customer = :1  AND email = :2 LIMIT 1",
                               contact.customer, contact.email)
        
        storedContact = contactQuery.get()

        if (storedContact):
            return "Contact already exists"
        else:
            return None
    def sendVerificationMessage(self, contact):
        message=mail.EmailMessage()
        message.sender=Constants().adminFrom()
        message.to=contact.email
        message.subject = "[imok] Are you willing to help monitor %s " %(contact.customer.name)
        htmlBody = self.getTemplate("email/new_contact_verification.txt", {'contact': contact})
        message.html=htmlBody
        message.body = html2text(htmlBody)
        message.send()
class UpdateContactHandler(ReqHandler):
    def update(self, status):
        contact_key = self.request.get('contactId')
        contact= db.get(db.Key(contact_key))
        if (contact):
            contact.status=status
            contact.put()
        values={
        'contact': contact,
        }            
        self.template("%s.html" % status, values)
            
class ContactDeclineHandler(UpdateContactHandler):
    def get(self):
        self.update('declined')
class ContactAcceptHandler(UpdateContactHandler):
    def get(self):
        self.update('active')
        
class DeleteContactHandler(ReqHandler):
    def get(self):
        contact_key = self.request.get('contactId')
        contact= db.get(db.Key(contact_key))
        message=None
        if (contact):
            contact.delete()
        else:
            message="No contact with that key"
        self.response.out.write(self.getJsonContacts(message))
        
        
### Web Handlers
class ListContactHandler(ReqHandler):
    def get(self):
        self.response.out.write(self.getJsonContacts(message=''))
        
class AlertPageHandler(ReqHandler):
    def get(self):
        alertId = self.request.get('alertId')
        (alertKey, a, alertCheck) = alertId.partition('-')
        key = db.Key.from_path('Alert', int(alertKey))
        alert= db.get(key)
        
        if (alertCheck == alert.check):
            values={'alert': alert}
            self.template('alert.html', values)
        else:
            self.error(404)
            self.template('alert_not_found.html', {})


#class FrontPageHandler(ReqHandler):
#    def get(self):
#        if (users.get_current_user()):
#            self.redirect('/account.html')
#        else:
#            self.template('index.html', {})

class FallbackHandler(ReqHandler):
  def get(self):
    template_name = 'index.html'
    values = {}
    url = self.request.path
    match = re.match("/(.*)$", url)
    if match:
        name=match.groups()[0]
        if name:
            template_name=name
            logging.debug ("template: %s" % template_name)
    account = self.getAccount()
    if (account):
        logging.debug('looking for notifications')
        notificationQuery = Notification.gql("WHERE customer =:1 ORDER BY dateTime DESC", account)
        notificationResults = notificationQuery.fetch(10)
        values={
        'notifications': notificationResults,
        'account': account,
        'customer': Constants().fakeCustomer(account),
        'alert': Constants().fakeAlert(account),
        'timeSinceNotification': (datetime.utcnow() - self.getAccount().lastNotificationDate)
        }            
    self.template(template_name, values)

def main():
  application = webapp.WSGIApplication(
                  [
                   # ('/signup/save/', SignupHandler),
                   #('/signup.html', SignupPageHandler),
                   ('/notify', WebNotificationHandler),
#                   ('/', FrontPageHandler),
                   ('/contact/list/', ListContactHandler),
                   ('/contact/add/', NewContactHandler),
                   ('/contact/delete/', DeleteContactHandler),
                   ('/contact/decline', ContactDeclineHandler),
                   ('/contact/accept', ContactAcceptHandler),
                   ('/settings/save/', SaveSettingsHandler),
                   ('/alert', AlertPageHandler),
                   ('/notification/', ExternalNotificationHandler),
                   ('.*', FallbackHandler),
                  ]
          )
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()