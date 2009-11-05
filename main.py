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
from util import *
from CustomerLogic import *


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


    def setCookie(self, key, value, expires=Constants().loginCookieExpiry()):
         simpleCookie = Cookie.SimpleCookie()

         simpleCookie[key] = str(base64.b64encode(value))
         simpleCookie[key]['expires'] = expires
         simpleCookie[key]['path'] = '/'
         #simpleCookie[key]['domain'] = Constants().domain()
         
         # Get the cookie without the header name as that is 
         # supplied to the add_header call separately.
         cookie = simpleCookie.output(header='')

         self.response.headers.add_header('Set-Cookie', cookie)

    def logout(self, sucessUrl):    
        cookieKey = self.getLoginCookie()
        if (cookieKey):
            accountKey = memcache.delete(cookieKey, namespace='imok-token')
        self.setCookie('imok-token', '', -99999)
        self.redirect(sucessUrl)
        
    def login(self, email, password, sucessUrl):    
        account= self.getAccountFromLogin(email, password)
        if (account):
            # create a cookie key
            rnd = random.random()
            id  = account.key().id()
            cookieKey = "%s-%s" %(rnd, id)
            # set the cookie on the web client
            logging.debug("setting cookie: imok-token=%s" % cookieKey)
            self.setCookie('imok-token', cookieKey)
            
            memcache.add(namespace='imok-token', key=cookieKey, value=account.key(), time=3600)
            self.redirect(sucessUrl)
        else:
            params={
                    'message' : "The email and password did not match",
                    'sucessUrl': sucessUrl,
            }
            url = "/login.html?%s" %(urllib.urlencode(params))
            self.redirect(url)
            
    def getAccountFromLogin(self, email, password):
        accountQuery = Customer.gql("WHERE email = :1 LIMIT 1",
                                   email)
        account = accountQuery.get()
        logging.debug("getAccountFromLogin email: %s"% str(email))
        if account:
            passwordHash = getHash(password, account.passwordSeed)
            if (passwordHash != account.passwordHash):
                logging.debug("password and password hash did not match")
                logging.debug("passwordHash: %s" % account.passwordHash)
                logging.debug("passwordSeed: %s" % account.passwordSeed)
                account = None
        return account
    def getLoginCookie(self):
        # get the cookie
        cookieKey =''
        try:
             cookieKey = str(base64.b64decode(self.request.cookies['imok-token']))
        except KeyError:
             #There wasn't a Cookie called that
             pass
        
        logging.debug("found cookie: imok-token=%s" % cookieKey)
        return cookieKey

    def getAccount(self, redirectOnFailure=True):
        cookieKey = self.getLoginCookie()
        # get the account from memcache
        account=None
        if (cookieKey):
            accountKey = memcache.get(cookieKey, namespace='imok-token')
            account=None
            if (accountKey):
                account = db.get(accountKey)
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
        values['domain'] = Constants().domain()
        account = values.get('account')
        if (account):
            values['logoutLink'] = '/logout/'
#            if account.username =='hamish' or account.username =='spacekate':
#                values['isAdmin'] = True
        path = os.path.join(os.path.dirname(__file__),'templates', templateName)
        return (template.render(path, values))

### Save Handlers
class NotificationHandler(ReqHandler):
    pass
#    def notify(self, vendorId, deviceId, customer=None):
#        now = datetime.utcnow()
#        if (customer):
#            self.notifyCustomer(customer, now)
#        else:
#            sourceQuery = Source.gql("WHERE vendorId =:1 and deviceId = :2 ", vendorId, deviceId)
#            sourceResults = sourceQuery.fetch(1)
#            for source in sourceResults:
#                self.notifyCustomer(source.customer, now)
#                customer=source.cutomer
#           
#        notification = Notification()
#        notification.vendorId = vendorId
#        notification.deviceId = deviceId
#        notification.dateTime=now
#        notification.customer=customer
#        notification.put()
#
#    def notifyCustomer(self, customer, time):
#        customer.notify(time)
#        customer.put()
#        alertQuery = Alert.gql("WHERE customer =:1 and closed = :2 LIMIT 1", customer, False)
#        alert = alertQuery.get()
#        if (alert):
#            alert.closed=True
#            alert.put()
class WebNotificationHandler(NotificationHandler):
    def process(self):
        customer = self.getAccount()
        logging.debug("Customer: %s" %str(customer))
        deviceId = str(customer.key().id())
        notify("website", deviceId, customer)
        
        self.redirect('/account.html')
        
class ExternalNotificationHandler(NotificationHandler):
    def process(self):
        vendorId = self.request.get('vendorId')
        deviceId = self.request.get('deviceId')
        notify(vendorId, deviceId)
        
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
class RegisterHandler(NotificationHandler):
    def process(self):
        # username = self.request.get('username')
        email = self.request.get('email')
        logging.debug("Register email: %s" % email)

        password = self.request.get('password')
        retypePassword = self.request.get('retypePassword')
#        passwordHash = getHash(password)
        name = self.request.get('name')
        sucessUrl= self.request.get('sucess_url')
        phone = self.request.get('phone')
        mobile = self.request.get('mobile')

        if (password != retypePassword):
            params={
                    'message' : Constants().passwordsDontMatchError(),
                    'sucessUrl': sucessUrl,
            }
            url = "/register.html?%s" %(urllib.urlencode(params))
            self.redirect(url)
            return
        try:
            createAccount(email, password, name, phone, mobile)
            self.login(email, password, sucessUrl)            
        except AccountExistsException, e:
            params={
                    'message' : "The email address has already been registered",
                    'sucessUrl': sucessUrl,
            }
            url = "/register.html?%s" %(urllib.urlencode(params))
            self.redirect(url)
        self.redirect(sucessUrl)

class LoginHandler(ReqHandler):
    def process(self):
        email = self.request.get('email')
        password = self.request.get('password')
        sucessUrl= self.request.get('sucess_url')
        self.login(email, password, sucessUrl)

class LogoutHandler(ReqHandler):
    def process(self):
        sucessUrl= self.request.get('sucess_url', '/index.html')
        self.logout(sucessUrl)
        

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
                   ('/logout/', LogoutHandler),
                   ('/register/', RegisterHandler),
                   ('/notification/', ExternalNotificationHandler),
                   ('.*', FallbackHandler),
                  ]
          )
    wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
    main()