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

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import urlfetch
from google.appengine.api import mail

class MainHandler(webapp.RequestHandler):
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
    path = os.path.join(os.path.dirname(__file__),'imok-core', template_name)
    self.response.out.write(template.render(path, values))

def main():
  application = webapp.WSGIApplication([('.*', MainHandler)])
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()