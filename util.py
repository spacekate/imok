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
    
def formatTimeDelta(delta):
    weeks, days = divmod(delta.days, 7)
    hours, remainder = divmod(delta.seconds, 3600)  
    minutes, seconds = divmod(remainder, 60)
    
    if weeks:
        return plural(weeks,'week') + ' ' + plural(days, 'day')
    if days:
        return plural(days,'day') + ' ' + plural(hours, 'hours')
    if hours:
        return plural(hours,'hour') + ' ' + plural(minutes, 'minute')
    if minutes:
        return plural(minutes,'minute') + ' ' + plural(seconds, 'second')
    return plural(seconds,'second')  