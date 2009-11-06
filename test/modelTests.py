import unittest
import logging
from google.appengine.ext import db
from models import *

class ModelTest(unittest.TestCase):

    def setUp(self):
        # Populate test entities if needed
        customer = Customer()
        customer.name   = 'test name'
        customer.phone  = 'phone'
        customer.mobile  = 'mobile'
        customer.email  = 'email'
        customer.timeout= 24*60
        customer.comment = 'comment'
    
        self.setup_key = customer.put()
        
    def tearDown(self):
          #The gaeunit library isolates the datastore 
          # instance from the main datastore and so 
          # is no need to delete test data. 
          pass
      
    def testAbc(self):
        customer = Customer()
        customer.username = "username"
        customer.passwordHash = "passwordHash"
        customer.name = "name"
        customer.email = "email"
        customer.timeout=24*60   #24 hours * 60 mins
        customer.phone="phone"
        customer.mobile="mobile"
        customer.comment=''
        customer.put()
          
    def testCustomerName(self):
        customer = Customer()
        customer.name="foo"
        self.assertEqual('foo', customer.name)
    
    def testSavedCustomer(self):
        customer = Customer(name='Foo')
        key = customer.put()
        self.assertEqual('Foo', db.get(key).name)
    
    def testSetupCustomer(self):
        customer = db.get(self.setup_key)
        self.assertEqual('test name', customer.name)
