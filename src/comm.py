#!/usr/bin/env python
from twisted.internet import reactor
from twisted.web import client
import urllib2
import simplejson
import observer
import model

def getAuthData(fileName):
    try:
        f = open(fileName)
        return simplejson.loads(f.read())
    except:
        print "error: getAuthData"

    return None

def printPage(data):
    print simplejson.loads(data)
    reactor.stop()

def printError(failure):
    print 'Error: %s' % failure.getErrorMessage()
    reactor.stop()

class Comm(observer.Listener):
    def __init__(self, fileName=None):
        if fileName != None:
            self.user = getAuthData(fileName)
        observer.Listener.__init__(self)
        self.session = model.startSession()

    def update(self, type, data):
        print type,",",data
        #reactor.stop()
        pass

    def get(self,errfunc = printError):

        u = urllib2.HTTPPasswordMgr()
        u.add_password('Twitter API', 'http://twitter.com/', 
                        self.user["user"], self.user["pass"])
        d = client.getPage('http://twitter.com/statuses/friends_timeline.json',
                        passwdMgr=u)
        d.addCallback(self.callback)
        d.addErrback(errfunc)
     
    def callback(self,data):
        # insert db and back twit data
        insertData = []
        for tw in simplejson.loads(data):
            insertData.append({"user": tw["user"]["screen_name"],
                               "text": tw["text"],
                               "time": tw["created_at"]})
            t = model.TwitData()
            t.user = tw["user"]["screen_name"]
            t.twit = tw["text"]
            t.time = tw["created_at"]
            self.session.save(t)

        #self.testDB()
        observer.notify("recent", insertData)


    def testDB(self):
        # test for db
        q = self.session.query(model.TwitData)
        for t in q:
            print t.user
            print t.twit
            print t.time
            print ""

def main():
    c = Comm("config.json")
    c.get()
    reactor.run()

if __name__ == "__main__":
    main()
