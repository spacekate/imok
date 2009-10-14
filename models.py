#!/usr/bin/env python
#
# I'm OK! website

from google.appengine.ext import db
from datetime import datetime, timedelta
from util import *
### Constants
END_OF_TIME=datetime.max
### Models
class Customer(db.Model):
    account = db.UserProperty()
    name = db.StringProperty()
    phone = db.StringProperty()
    mobile = db.StringProperty()
    email = db.EmailProperty()
    comment = db.StringProperty(multiline=True)
    timeout = db.IntegerProperty()
    creationDate = db.DateTimeProperty(auto_now_add=True)
    lastNotificationDate = db.DateTimeProperty()
    notificationTime = db.DateTimeProperty()
    alertSent = db.BooleanProperty()
    
    def timeSinceNotification(self):
        return formatTimeDelta(datetime.utcnow() - self.lastNotificationDate)
   
    def notify(self):
        self.lastNotificationDate = datetime.utcnow()
        if (self.timeout == -1):
            self.notificationTime = END_OF_TIME
        else :
            self.notificationTime = self.lastNotificationDate + timedelta(minutes=self.timeout)
        self.alertSent = False 
        
class Notification(db.Model):
    dateTime = db.DateTimeProperty()
    vendorId = db.StringProperty()
    deviceId = db.StringProperty()
    customer=db.ReferenceProperty(Customer)
    def timeSinceNotification(self):
        return abbreviatedTimeDelta(datetime.utcnow() - self.dateTime)
#    def notificationTime(self):
#        return formatTimeWithReference(datetime.utcnow(), self.dateTime)
    
class Source(db.Model):
    customer=db.ReferenceProperty(Customer)
    vendorId = db.StringProperty()
    deviceId = db.StringProperty()
        
class Contact(db.Model):
    customer=db.ReferenceProperty(Customer)
    email = db.EmailProperty()
    status = db.StringProperty(choices=set(["active", "pending", "declined"]))

class Alert(db.Model):
    customer=db.ReferenceProperty(Customer)
    creationDate = db.DateTimeProperty(auto_now_add=True)
    check = db.StringProperty()
    closed = db.BooleanProperty()
    
    