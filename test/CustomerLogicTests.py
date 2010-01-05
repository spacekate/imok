import unittest
#import logging
from util import *
from CustomerLogic import *

class CustomerLogicTest(unittest.TestCase):
    def testCreate(self):
        createAccount('e@currie.to', 'p', 'n', 'ph', 'mob')
        try:
            createAccount('e@currie.to', 'p', 'n', 'ph', 'mob')
            self.fail('Should not have been allowed to create 2 accounts with same username')
        except AccountExistsException, e:
            pass
