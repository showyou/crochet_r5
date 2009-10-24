#!/usr/bin/env python
# -*- coding: utf-8 -*-
import wx
import wx.aui
import wx.lib.ClickableHtmlWindow
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin

from twisted.internet import wxreactor
wxreactor.install()
from twisted.internet import reactor
from twisted.web import client
import simplejson

import observer
import comm

ID_EXIT = 101

"""自動リサイズするListCtrl"""
class ListCtrlAutoWidth(wx.ListCtrl, ListCtrlAutoWidthMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self,parent,style=wx.LC_REPORT|wx.LC_HRULES
                              |wx.LC_SINGLE_SEL)
        ListCtrlAutoWidthMixin.__init__(self)

class TmpTwitPage(wx.NotebookPage):
    def __init__(self, title, parent):
        self.count = 0
        self.selectedRow = 0
        self.title = title
        self.owner = parent
        wx.NotebookPage.__init__(self,parent.getNotebook(),-1)
        
        parent.getNotebook().AddPage(self,title)
        
        list = self.list = ListCtrlAutoWidth(self)
        #list.Bind(wx.EVT_KEY_DOWN, self.myKeyHandler)
        #list.Bind(wx.EVT_LIST_ITEM_ACTIVATED,self.OnDoubleClick)
        
        list.InsertColumn(0," ",1,20)
        list.InsertColumn(1,u"ユーザ")
        list.InsertColumn(2,u"発言",width=300)
        list.InsertColumn(3,u"時刻",width=60);
        #list.Bind(wx.EVT_LIST_ITEM_SELECTED,self.OnTwitListSelect)

        #a = self.imageListProxy = ImageListProxy()
        #list.AssignImageList( a.imageList, wx.IMAGE_LIST_SMALL)


class RecentPage(TmpTwitPage):
    """
    最近のfriendsの発言一覧を表示するページ
    """
    def __init__(self, parent,filter):
        TmpTwitPage.__init__(self,u"最新",parent)

class TwitHtml(wx.lib.ClickableHtmlWindow.PyClickableHtmlWindow):
    def __init__(self, parent):
        wx.lib.ClickableHtmlWindow.PyClickableHtmlWindow.__init__(self,parent,-1,size=(90,50),style=wx.VSCROLL)

    def SetValue(self, text):
        self.SetPage(text)
        pass

class MyFrame(wx.Frame, observer.Listener):
    TIMER_ID = 1
    def __init__(self, parent, ID, title):
        wx.Frame.__init__(self, parent, ID, title,
                wx.DefaultPosition, wx.Size(300,200))
        observer.Listener.__init__(self)
 
        self.c = comm.Comm("config.json")
        menu = wx.Menu()
        menu.Append(ID_EXIT, "E&xit", "Terminate the program")
        menuBar = wx.MenuBar()
        menuBar.Append(menu, "&File");
       
        text = self.text = wx.TextCtrl(self,-1,style=wx.TE_PROCESS_ENTER)
        #text.Bind(wx.EVT_TEXT_ENTER, self.OnSendTW)
        button = self.button = wx.Button(self, -1, "Send") 
        #self.button.Bind(wx.EVT_BUTTON, self.OnSendTW)
        
        notebook = self.notebook = wx.aui.AuiNotebook(
                                    self,
                                    -1,
                                    style= wx.aui.AUI_NB_BOTTOM |
                                           wx.aui.AUI_NB_WINDOWLIST_BUTTON|
                                           wx.aui.AUI_NB_TAB_SPLIT
                                   )

        filter = None
        self.recentPage = RecentPage(self,filter)
        #self.replyPage = ReplyPage(self,self.httpThreadLock)
        #self.directPage = DMPage(self,self.httpThreadLock)

        #for p in twTabConfig['tabName']:
        #    page = CustomPage(p,self,self.httpThreadLock)
        #    self.recentPage.AppendCustomPage(page,p)

        inputSizer = wx.BoxSizer(wx.HORIZONTAL)
        inputSizer.Add(self.text,2)
        inputSizer.Add(self.button,0)

        #messageText=self.messageText = wx.TextCtrl(self,-1,style=wx.TE_MULTILINE|wx.TE_AUTO_URL|wx.TE_READONLY,size=(-1,65))
        messageText = self.messageText = TwitHtml(self)
        userIcon = self.userIcon = wx.StaticBitmap(self,-1,wx.NullBitmap,(0,0),(64,64))
        userName = self.userName = wx.StaticText(self,-1,"test")
        twitTime = self.twitTime = wx.StaticText(self,-1,"---")

        messageSizer3 = wx.BoxSizer(wx.HORIZONTAL)
        messageSizer3.Add(userName,2,wx.EXPAND)
        messageSizer3.Add(twitTime,3,wx.EXPAND,wx.ALIGN_RIGHT)

        messageSizer2 = wx.BoxSizer(wx.VERTICAL)
        messageSizer2.Add(messageSizer3,0,wx.EXPAND)
        messageSizer2.Add(messageText,0,wx.EXPAND)

        messageSizer1 = wx.BoxSizer(wx.HORIZONTAL)
        messageSizer1.Add(userIcon,0,wx.EXPAND)
        messageSizer1.Add(messageSizer2,1,wx.EXPAND)

        messageSizer = wx.BoxSizer(wx.VERTICAL)
        messageSizer.Add(messageSizer1,0,wx.EXPAND)
        messageSizer.Add(inputSizer,0,wx.EXPAND)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(notebook,2,wx.EXPAND)
        self.sizer.Add(messageSizer,0,wx.EXPAND)
        
        self.SetSizer(self.sizer)
        self.SetAutoLayout(True)
        inputSizer.Fit(self)
        self.sizer.Fit(self)

        self.x = wx.StaticText(self, -1, '-')
        self.SetMenuBar(menuBar)
        wx.EVT_MENU(self, ID_EXIT,self.DoExit)

        self.timer = self.startTimer(self.TIMER_ID,self.OnUpdate,20000)
        self.CreateStatusBar()

        print "loading MyFrame"
        self.setStatusBar("start")

    def getNotebook(self):
        return self.notebook

    def DoExit(self, event):
        self.Close(True)
        reactor.stop()

    def setStatusBar(self,str):
        sb = wx.GetApp().GetTopWindow().GetStatusBar()
        sb.SetStatusText(str)
        print "setStatusBar %s" %str

    def startTimer(self, timerID, func, span):
        timer = wx.Timer(self,timerID)
        wx.EVT_TIMER(self,timerID,func)
        timer.Start(span)
        return timer

    def OnUpdate(self,event):

        self.c.get()
        self.setStatusBar("start: getPage")

    def update(self, type, data):
        print data
        self.x.SetLabel(type)
        self.setStatusBar("end: getPage")


class MyApp(wx.App):
    def __init__(self):
        wx.App.__init__(self, False)
        self.frame = MyFrame(None, -1, "Hello, world")
        self.frame.Show(True)
        self.SetTopWindow(self.frame)


def main():
    app = MyApp()
    reactor.registerWxApp(app)
    reactor.run()

if __name__ == "__main__":
    main()
