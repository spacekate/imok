import unittest
#import logging
from util import *
from CustomerLogic import *

class CustomerLogicTest(unittest.TestCase):     
    def testCreate(self):
        createAccount('u', 'p', 'n', 'e@currie.to', 'ph', 'mob')
        try:
            createAccount('u', 'p', 'n', 'e@currie.to', 'ph', 'mob')
            self.fail('Should not have been allowed to create 2 accounts with same username')
        except AccountExistsException, e:
            pass
