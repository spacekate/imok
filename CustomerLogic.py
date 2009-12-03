
from google.appengine.ext import db

from util import *
from models import *


class AccountExistsException(Exception):
    pass

def notify(vendorId, deviceId, customer=None):
    result=0
    now = datetime.utcnow()
    if (customer):
        notifyCustomer(customer, now)
        result=1
    else:
        sourceQuery = Source.gql("WHERE vendorId =:1 and deviceId = :2 ", vendorId, deviceId)
        sourceResults = sourceQuery.fetch(1)
        for source in sourceResults:
            notifyCustomer(source.customer, now)
            customer=source.customer
            result=result+1
       
    notification = Notification()
    notification.vendorId = vendorId
    notification.deviceId = deviceId
    notification.dateTime=now
    notification.customer=customer
    notification.put()
    return result

def notifyCustomer(customer, time):
    customer.notify(time)
    customer.put()
    alertQuery = Alert.gql("WHERE customer =:1 and closed = :2 LIMIT 1", customer, False)
    alert = alertQuery.get()
    if (alert):
        alert.closed=True
        alert.put()

def createAccount(email, password, name,  phone, mobile):

        accountQuery = Customer.gql("WHERE email = :1 LIMIT 1",
                                   email)
        account = accountQuery.get()
        if (not account):
            passwordSeed = getSeed()
            passwordHash = getHash(password, passwordSeed)

            customer = Customer()
            customer.email = email
            customer.passwordHash = passwordHash
            customer.passwordSeed = passwordSeed
            customer.name = name
            customer.timeout=24*60   #24 hours * 60 mins
            customer.phone=phone
            customer.mobile=mobile
            customer.comment=''
            customer.put()
            
            # create source record
            createSource(customer)
            vendorId = "website"
            deviceId = str(customer.key().id())
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