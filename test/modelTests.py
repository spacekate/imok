import unittest
import logging
from google.appengine.ext import db
import models

class ModelTest(unittest.TestCase):

  def setUp(self):
    # Populate test entities if needed
    c = models.Customer(name='Bar')
    self.setup_key = c.put()
    
  def tearDown(self):
    # There is no need to delete test entities.
    pass

  def testCustomerName(self):
    customer = models.Customer()
    customer.name="foo"
    self.assertEqual('foo', customer.name)

  def testSavedCustomer(self):
    customer = models.Customer(name='Foo')
    key = customer.put()
    self.assertEqual('Foo', db.get(key).name)

  def testSetupCustomer(self):
    customer = db.get(self.setup_key)
    self.assertEqual('Bar', customer.name)
