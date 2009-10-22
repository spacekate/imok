import unittest
#import logging
from util import *
from datetime import timedelta

class ModelTest(unittest.TestCase):     
    def testPlural(self):
        word = 'word'
        self.assertEqual('0 words', plural(0, word))
        self.assertEqual('1 word', plural(1, word))
        self.assertEqual('2 words', plural(2, word))
    def testTimeDelta(self):
        year = timedelta(days=365)
        self.assertEqual('52 weeks 1 day', formatTimeDelta(year))
        
        a = timedelta(weeks=40, days=1, hours=23, minutes=10, seconds=7)
        b = timedelta(days=1, hours=23, minutes=10, seconds=7)
        c = timedelta(hours=23, minutes=10, seconds=7)
        d = timedelta(minutes=10, seconds=7)
        e = timedelta(seconds=7)
        
        self.assertEqual('40 weeks 1 day', formatTimeDelta(a))
        self.assertEqual('1 day 23 hours', formatTimeDelta(b))
        self.assertEqual('23 hours 10 minutes', formatTimeDelta(c))
        self.assertEqual('10 minutes 7 seconds', formatTimeDelta(d))
        self.assertEqual('7 seconds', formatTimeDelta(e))

        self.assertEqual('40 weeks 1 day', abbreviatedTimeDelta(a))
        self.assertEqual('1 day 23 hours', abbreviatedTimeDelta(b))
        self.assertEqual('23 hours 10 mins', abbreviatedTimeDelta(c))
        self.assertEqual('10 mins 7 secs', abbreviatedTimeDelta(d))
        self.assertEqual('7 secs', abbreviatedTimeDelta(e))
