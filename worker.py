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
from main import *

class WorkerHandler(ReqHandler):
    def get(self):
        idleCustomers = Customer.gql("WHERE notificationTime <= :1 AND alertSent = False ",
                               datetime.utcnow())
        for customer in idleCustomers:
            self.handleIdleCustomer(customer)
        self.response.out.write("worker finished")

    def handleIdleCustomer(self, customer):
        for contact in customer.contact_set:
            message=mail.EmailMessage()
            message.sender='hcurrie@gmail.com'
            message.to=contact.email
            message.subject = "[imok] Have you spoken to %s recently?" %(customer.name)
            message.body=self.getTemplate("email/alert_email.txt", {'customer': customer})
            message.send()
            self.response.out.write("worker sent email to %s for %s</br>" %(contact.email, customer.email))
        customer.alertSent=True
        customer.put()
        


def main():
  application = webapp.WSGIApplication(
                  [('/worker/', WorkerHandler),
                  ]
          )
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()