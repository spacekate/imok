#!/usr/bin/env python
#
# I'm OK! website

from google.appengine.ext import db
from datetime import datetime, timedelta

### Models
class Customer(db.Model):
    account = db.UserProperty()
    name = db.StringProperty()
#    firstName = db.StringProperty()
#    lastName = db.StringProperty()
    email = db.EmailProperty()
    creationDate = db.DateTimeProperty(auto_now_add=True)
    lastNotificationDate = db.DateTimeProperty()
    notificationTime = db.DateTimeProperty()

    def notify(self):
        self.lastNotificationDate = datetime.utcnow()
        self.notificationTime = self.lastNotificationDate + timedelta(minutes=2) 

class Contact(db.Model):
    customer=db.ReferenceProperty(Customer)
    email = db.EmailProperty()
    