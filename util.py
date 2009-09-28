def plural(num, word):
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