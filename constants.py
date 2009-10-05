import os

class Constants():
    def domain(self):
        domain = os.environ['HTTP_HOST']
        if (not domain):
            domain = "i-am-ok.appspot.com"
        return domain