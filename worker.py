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
import random


from datetime import datetime

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import urlfetch
from google.appengine.api import mail

from html2text import html2text

from models import *
from main import *

class WorkerHandler(ReqHandler):
    def get(self):
        idleCustomers = Customer.gql("WHERE notificationTime <= :1 AND alertSent = False ",
                               datetime.utcnow())
        
        for customer in idleCustomers:
            self.handleIdleCustomer(customer, str(random.randint(1, 9999)))
        self.response.out.write("worker finished<br /><a href='/'>Return to App</a>")

    def handleIdleCustomer(self, customer, check):
        # Create alert
        alert=Alert()
        alert.customer=customer
        alert.check = check
        alert.closed=False
        alert.put()
        # email alert
        for contact in customer.contact_set:
            message=mail.EmailMessage()
            message.sender=Constants().adminFrom()
            message.to=contact.email
            message.subject = "[imok] Have you spoken to %s recently?" %(customer.name)
            htmlBody = self.getTemplate("email/alert_email.txt", {'customer': customer, 'alert': alert})
            message.html=htmlBody
            message.body = html2text(htmlBody)
            message.send()
            self.response.out.write("worker sent email to %s for %s</br>" %(contact.email, customer.email))
            self.response.out.write("<hr><pre>%s</pre><hr></br>" %(message.body))
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