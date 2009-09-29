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

from datetime import datetime

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import urlfetch
from google.appengine.api import mail

from models import *

### Base Classes
class ReqHandler(webapp.RequestHandler):
    def getAccount(self):
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
            contacts.append( {'email': contact.email, 'key': str(contact.key())})
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
        path = os.path.join(os.path.dirname(__file__),'templates', templateName)
        return (template.render(path, values))

### Save Handlers
class NotificationHandler(ReqHandler):
    def get(self):
        customer = self.getAccount()
        customer.notify()
        customer.put()
        alertQuery = Alert.gql("WHERE customer =:1 and closed = :2 LIMIT 1", customer, False)
        alert = alertQuery.get()
        if (alert):
            alert.closed=True
            alert.put()
        self.redirect('/account.html')
        
class ExternalNotificationHandler(ReqHandler):
    def get(self):
        notification = Notification()
        notification.vendorId = self.request.get('vendorId')
        notification.deviceId = self.request.get('deviceId')
        notification.dateTime=datetime.utcnow()
        notification.put()
        
        # Find the customer(s) with the given source and notify them.
        sourceQuery = Source.gql("WHERE vendorId =:1 and deviceId = :2 ", notification.vendorId, notification.deviceId)
        sourceResults = sourceQuery.fetch(50)
        for source in sourceResults:
            source.customer.notify()
            source.customer.put()
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
        
class NewContactHandler(ReqHandler):
    def get(self):
        contact = Contact()
        contact.customer=self.getAccount()
        contact.email=self.request.get('newContact')
        message=self.verifyContact(contact)
        if (not message):
            contact.put()
        self.response.out.write(self.getJsonContacts(message))
        
    def verifyContact(self, contact):
        contactQuery = Contact.gql("WHERE customer = :1  AND email = :2 LIMIT 1",
                               contact.customer, contact.email)
        
        storedContact = contactQuery.get()
        #storedContact = Contact(email='contact.email', customer=contact.customer)
        #pet = Pet(name="Fluffy", owner=owner)

        if (storedContact):
            return "Contact already exists"
        else:
            return None
        
        
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
class AccountHandler(ReqHandler):
    def get(self):
        account = self.getAccount()
        if (account):
            values={
            'account': account,
            'timeSinceNotification': (datetime.utcnow() - self.getAccount().lastNotificationDate)
            }
            self.template('account.html', values)
        else:
            self.redirect('/signup.html')

class FrontPageHandler(ReqHandler):
    def get(self):
        if (users.get_current_user()):
            self.redirect('/account.html')
        else:
            self.template('index.html', {})

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
        # create fake customer to be used on the settings page
        fakeCustomer = {'name': '<span name="nameSample"></span>',
                'timeSinceNotification': '<span name="timeoutSample"></span>',
                'phone': '<span name="phoneSample"></span>',
                'mobile': '<span name="mobileSample"></span>',
                'comment': '<textarea id="comment" name="comment" class="comment" rows="10" cols="10">%s</textarea>' % account.comment,
                }
        values={
        'account': account,
        'customer': fakeCustomer,
        'timeSinceNotification': (datetime.utcnow() - self.getAccount().lastNotificationDate)
        }            
    self.template(template_name, values)

def main():
  application = webapp.WSGIApplication(
                  [
                   # ('/signup/save/', SignupHandler),
                   #('/signup.html', SignupPageHandler),
                   ('/notify', NotificationHandler),
                   ('/', FrontPageHandler),
                   ('/account.html', AccountHandler),
                   ('/contact/list/', ListContactHandler),
                   ('/contact/add/', NewContactHandler),
                   ('/contact/delete/', DeleteContactHandler),
                   ('/settings/save/', SaveSettingsHandler),
                   ('/alert', AlertPageHandler),
                   ('/notification/', ExternalNotificationHandler),
                   ('.*', FallbackHandler),
                  ]
          )
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()