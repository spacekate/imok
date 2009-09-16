#!/usr/bin/env python
#
# I'm OK! website

from google.appengine.ext import db
from datetime import datetime, timedelta

### Models
class Customer(db.Model):
    account = db.UserProperty()
    name = db.StringProperty()
    email = db.EmailProperty()
    timeout = db.IntegerProperty()
    creationDate = db.DateTimeProperty(auto_now_add=True)
    lastNotificationDate = db.DateTimeProperty()
    notificationTime = db.DateTimeProperty()
    alertSent = db.BooleanProperty()

    def notify(self):
        self.lastNotificationDate = datetime.utcnow()
        self.notificationTime = self.lastNotificationDate + timedelta(minutes=self.timeout)
        #self.notificationTime = self.lastNotificationDate + timedelta(minutes=1)
        self.alertSent = False 

class Contact(db.Model):
    customer=db.ReferenceProperty(Customer)
    email = db.EmailProperty()
    