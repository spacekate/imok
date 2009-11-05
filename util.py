import hashlib
import random
from constants import *

def plural(num, word):
    # Simplified code based upon:
    # http://code.activestate.com/recipes/82102/
    # In future a more complete implementation may be based upon 
    # http://owl.english.purdue.edu/handouts/grammar/g_spelnoun.html
    # http://grammar.ccc.commnet.edu/grammar/plurals.htm
    if num == 1:
        return '%s %s' %(num, word)
    else: 
        return '%s %s%s' %(num, word, 's')
    
def formatTimeDelta(delta, weekLabel='week', dayLabel='day', hourLabel='hour', minLabel='minute', secLabel='second'):
    weeks, days = divmod(delta.days, 7)
    hours, remainder = divmod(delta.seconds, 3600)  
    minutes, seconds = divmod(remainder, 60)
    
    if weeks:
        return plural(weeks,weekLabel) + ' ' + plural(days, dayLabel)
    if days:
        return plural(days,dayLabel) + ' ' + plural(hours, hourLabel)
    if hours:
        return plural(hours,hourLabel) + ' ' + plural(minutes, minLabel)
    if minutes:
        return plural(minutes,minLabel) + ' ' + plural(seconds, secLabel)
    return plural(seconds,secLabel)

def abbreviatedTimeDelta(delta):
    return formatTimeDelta(delta, minLabel='min', secLabel='sec')

def getHash(word, seed=None):
    #return hashlib.sha224(word).hexdigest()
    hash = hashlib.sha512()
    if seed:
        hash.update(seed)
    hash.update(word)
    return hash.hexdigest()

def getSeed():
    c=Constants()
    seed=random.choice(c.alphaNum()) + \
         random.choice(c.alphaNum()) + \
         random.choice(c.alphaNum()) + \
         random.choice(c.alphaNum())
    return seed
#def formatTimeWithReference(reference, theTime):
#    delta = reference.date() - theTime.date()
#    deltaDays = delta.days
#    if (deltaDays==0):
#        return theTime.strftime("Today %I:%M %p")
#    if (deltaDays==1):
#        return theTime.strftime("Yesterday %I:%M %p")
#    if (deltaDays >0 and deltaDays < 7):
#        return theTime.strftime("%A %I:%M %p")
#    else:
#        return theTime.strftime("%A %d %b %I:%M %p")    
#    