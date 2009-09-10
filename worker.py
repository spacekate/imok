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

class WorkerHandler(webapp.RequestHandler):
    def get(self):
        idleCustomers = Customer.gql("WHERE notificationTime > :1 ",
                               datetime.utcnow())
        for customer in idleCustomers:
            self.response.out.write(customer.firstName + "</br>")
        self.response.out.write("worker")


def main():
  application = webapp.WSGIApplication(
                  [('/worker/', WorkerHandler),
                  ]
          )
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()