class Listener(object):
    def __init__(self):
       s.addListener(self)
   
    def update(self,type,data):
       print "update",data

class _Subject(object):
    def __init__(self):
        self.listeners = []
    
    def addListener(self, listener):
        self.listeners.append(listener)

    def notifySignal(self, type, data):
        for l in self.listeners:
            l.update(type, data)

s = _Subject() 
def notify(type, data):
    s.notifySignal(type, data)
