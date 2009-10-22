import unittest
import logging
from util import *

class ModelTest(unittest.TestCase):

    def setUp(self):
    	pass
    	
    def tearDown(self):
          #The gaeunit library isolates the datastore 
          # instance from the main datastore and so 
          # is no need to delete test data. 
          pass
      
    def testPlural(self):
        word = 'word'
        self.assertEqual('0 words', plural(0, word))
        self.assertEqual('1 word', plural(1, word))
        self.assertEqual('2 words', plural(2, word))

