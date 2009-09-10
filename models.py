#!/usr/bin/env python
#
# I'm OK! website

from google.appengine.ext import db

### Models
class Customer(db.Model):
    account = db.UserProperty()
    firstName = db.StringProperty()
    lastName = db.StringProperty()
    email = db.EmailProperty()
    creationDate = db.DateTimeProperty(auto_now_add=True)
    lastNotificationDate = db.DateTimeProperty()
class Contact(db.Model):
    customer=db.ReferenceProperty(Customer)
