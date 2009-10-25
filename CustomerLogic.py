
from google.appengine.ext import db

from util import *
from models import *


class AccountExistsException(Exception):
    pass

def notify(vendorId, deviceId, customer=None):
    now = datetime.utcnow()
    if (customer):
        notifyCustomer(customer, now)
    else:
        sourceQuery = Source.gql("WHERE vendorId =:1 and deviceId = :2 ", vendorId, deviceId)
        sourceResults = sourceQuery.fetch(1)
        for source in sourceResults:
            notifyCustomer(source.customer, now)
            customer=source.customer
       
    notification = Notification()
    notification.vendorId = vendorId
    notification.deviceId = deviceId
    notification.dateTime=now
    notification.customer=customer
    notification.put()

def notifyCustomer(customer, time):
    customer.notify(time)
    customer.put()
    alertQuery = Alert.gql("WHERE customer =:1 and closed = :2 LIMIT 1", customer, False)
    alert = alertQuery.get()
    if (alert):
        alert.closed=True
        alert.put()

def createAccount(username, password, name, email, phone, mobile):
        passwordHash = getHash(password)

        accountQuery = Customer.gql("WHERE username = :1 LIMIT 1",
                                   username)
        account = accountQuery.get()
        if (not account):
            customer = Customer()
            customer.username = username
            customer.passwordHash = passwordHash
            customer.name = name
            customer.email = email
            customer.timeout=24*60   #24 hours * 60 mins
            customer.phone=phone
            customer.mobile=mobile
            customer.comment=''
            #customer.notify()
            customer.put()
            vendorId = "website"
            deviceId = str(customer.key().id())

            # create source record
            createSource(customer)
#            source = Source()
#            source.customer=customer
#            source.vendorId = vendorId
#            source.deviceId = deviceId
#            source.put()
            
            notify("website", deviceId)

        else:
            raise AccountExistsException()
def createSource(customer):
            vendorId = "website"
            deviceId = str(customer.key().id())

            # create source record
            source = Source()
            source.customer=customer
            source.vendorId = vendorId
            source.deviceId = deviceId
            source.put()    