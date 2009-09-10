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
        account = Customer.gql("WHERE account = :1 LIMIT 1",
                               users.get_current_user())
        return account.get()
    def template(self, templateName, values):
        if (users.get_current_user()):
            values['logoutLink'] = users.create_logout_url("/")            
        path = os.path.join(os.path.dirname(__file__),'templates', templateName)
        self.response.out.write(template.render(path, values))

### Save Handlers
class SignupHandler(webapp.RequestHandler):
    def post(self):
        customer = Customer()
        customer.account = users.get_current_user()
        customer.firstName = self.request.get('firstName')
        customer.lastName = self.request.get('lastName')
        customer.email = self.request.get('email')
        customer.lastNotificationDate=datetime.utcnow()
        customer.put()
        self.redirect('/account.html')

class NotificationHandler(ReqHandler):
    def get(self):
        customer = self.getAccount()
        customer.lastNotificationDate=datetime.utcnow()
        customer.put()
        self.redirect('/account.html')

### Web Handlers
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

class SignupPageHandler(ReqHandler):
    def get(self):
        if (users.get_current_user()):
            if (self.getAccount()):
                self.redirect('/account.html')
            else:
                self.template('signup.html',{})
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
    self.template(template_name, values)

def main():
  application = webapp.WSGIApplication(
                  [('/signup/save/', SignupHandler),
                   ('/notify', NotificationHandler),
                   ('/', FrontPageHandler),
                   ('/signup.html', SignupPageHandler),
                   ('/account.html', AccountHandler),
                   ('.*', FallbackHandler),
                  ]
          )
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()