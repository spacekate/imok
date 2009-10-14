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
import random
import base64
import Cookie

from datetime import datetime
from html2text import html2text

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import urlfetch
from google.appengine.api import mail
from google.appengine.api import memcache

from models import *
from constants import *

### Base Classes
class RedirectException(Exception):
     def __init__(self, url):
         self.url = url
     def __str__(self):
         return repr(self.url)
     
class ReqHandler(webapp.RequestHandler):
    def post(self):
        self.get()
    def get(self):
        try:
            self.process()
        except RedirectException, e:
            self.redirect(e.url)

    def setCookie(self, key, value, ):
         simpleCookieObj = Cookie.SimpleCookie()

         simpleCookieObj[key] = str(base64.b64encode(value))
         simpleCookieObj[key]['expires'] = 360
         simpleCookieObj[key]['path'] = '/'
         #simpleCookieObj[key]['domain'] = self.domain
         #simpleCookieObj[key]['secure'] = ''

         #Cookie.SimpleCookie's output doesn't seem to be compatible with WebApps's http header functions
         #and this is a dirty fix
         headerStr = simpleCookieObj.output()
         regExObj = re.compile('^Set-Cookie: ')
         cookie = str(regExObj.sub('', headerStr, count=1))
         self.response.headers.add_header('Set-Cookie', cookie)

        
    def login(self, username, password, sucessUrl):    
        account= self.getAccountFromLogin(username, password)
        if (account):
            # create a cookie key
            rnd = random.random()
            id  = account.key().id()
            cookieKey = "%s-%s" %(rnd, id)
            # set the cookie on the web client
            logging.debug("setting cookie: imok-token=%s" % cookieKey)
            self.setCookie('imok-token', cookieKey)
            
            memcache.add(namespace='imok-token', key=cookieKey, value=account, time=3600)
            self.redirect(sucessUrl)
        else:
            params={
                    'message' : "The username and pssword did not match",
                    'sucessUrl': sucessUrl,
            }
            url = "/login.html?%s" %(urllib.urlencode(params))
            self.redirect(url)
            
    def getAccountFromLogin(self, username, password):
        accountQuery = Customer.gql("WHERE username = :1 LIMIT 1",
                                   username)
        account = accountQuery.get()
        return account
    def getAccount(self, redirectOnFailure=True):
        # get the cookie
        cookieKey =''
        try:
             cookieKey = str(base64.b64decode(self.request.cookies['imok-token']))
        except KeyError:
             #There wasn't a Cookie called that
             pass
        
        logging.debug("found cookie: imok-token=%s" % cookieKey)

        # get the account from memcache
        account=None
        if (cookieKey):
            account = memcache.get(cookieKey, namespace='imok-token')
        if (account):
            return account
        if (redirectOnFailure):
            self.redirectToLogin("/account.html", "login timed out")
        else:
            return None

    def redirectToLogin(self, sucessUrl, message=''):
            params={
                    'message' : message,
                    'sucessUrl': sucessUrl,
            }
            url = "/login.html?%s" %(urllib.urlencode(params))
            raise RedirectException(url)
            #self.redirect(url)      
    
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
    def process(self):
        customer = self.getAccount()
        logging.debug("Customer: %s" %str(customer))
        deviceId = str(customer.key().id())
        self.notify("website", deviceId, customer)        
        self.redirect('/account.html')
        
class ExternalNotificationHandler(NotificationHandler):
    def process(self):
        vendorId = self.request.get('vendorId')
        deviceId = self.request.get('deviceId')
        self.notify(vendorId, deviceId)
        
        self.redirect('/account.html')
        
class SaveSettingsHandler(ReqHandler):
    def process(self):
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
    def process(self):
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
    def process(self):
        self.update('declined')
class ContactAcceptHandler(UpdateContactHandler):
    def process(self):
        self.update('active')
        
class DeleteContactHandler(ReqHandler):
    def process(self):
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
    def process(self):
        self.response.out.write(self.getJsonContacts(message=''))
        
class AlertPageHandler(ReqHandler):
    def process(self):
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
#    def process(self):
#        if (users.get_current_user()):
#            self.redirect('/account.html')
#        else:
#            self.template('index.html', {})
class RegisterHandler(ReqHandler):
    def process(self):
        username = self.request.get('username')
        password = self.request.get('password')
        name = self.request.get('name')
        email = self.request.get('email')
        sucessUrl= self.request.get('sucess_url')

        accountQuery = Customer.gql("WHERE username = :1 LIMIT 1",
                                   username)
        account = accountQuery.get()        
        if (not account):
            customer = Customer()
            customer.username = username
            customer.password = password
            customer.name = name
            customer.email = email
            customer.timeout=24*60   #24 hours * 60 mins
            customer.phone=''
            customer.mobile=''
            customer.comment=''
            customer.notify()
            customer.put()
            account=customer
            self.redirect(sucessUrl)
        else:
            params={
                    'message' : "The username is already in use",
                    'sucessUrl': sucessUrl,
            }
            url = "/register.html?%s" %(urllib.urlencode(params))
            self.redirect(url)            
class LoginHandler(ReqHandler):
    def process(self):
        username = self.request.get('username')
        password = self.request.get('password')
        sucessUrl= self.request.get('sucess_url')
        self.login(username, password, sucessUrl)
        

class FallbackHandler(ReqHandler):
    def process(self):
        authRequired = ('account.html', 'settings.html')
        template_name = 'index.html'
        values = {}
        url = self.request.path
        match = re.match("/(.*)$", url)
        if match:
            name=match.groups()[0]
            if name:
                template_name=name
                logging.debug ("template: %s" % template_name)
        account = self.getAccount(redirectOnFailure=False)
        if (not account and template_name in authRequired):
            self.redirectToLogin("/%s"%template_name, "login required")
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
        values['args'] = self.getArgs() 
        self.template(template_name, values)

    def getArgs(self):
        args={}
        for i in self.request.arguments():
            args[i] = self.request.get(i)
        return args

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
                   ('/login/', LoginHandler),
                   ('/register/', RegisterHandler),
                   ('/notification/', ExternalNotificationHandler),
                   ('.*', FallbackHandler),
                  ]
          )
    wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
    main()