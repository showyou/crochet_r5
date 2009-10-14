#! -*- coding:utf-8 -*-
#! 外見に関するところを書く
import os
import sys
import wx.aui

import wx
import wx.lib.ClickableHtmlWindow
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin

#自動で chdirし，working directory を crochet のあるディレクトリにする
#dir = os.path.split(sys.argv[0])[0]
#os.chdir(dir)

try:
    import Growl
    g_growl = True
except:
    print "not exist:Growl sdk"
    g_growl = False

"""自動リサイズするListCtrl"""
class ListCtrlAutoWidth(wx.ListCtrl, ListCtrlAutoWidthMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self,parent,
                             style=wx.LC_REPORT|wx.LC_HRULES|wx.LC_SINGLE_SEL)
        ListCtrlAutoWidthMixin.__init__(self)


class TmpTwitPage(wx.NotebookPage):
    """
    全てのnotebookpageの基になるページクラス
    """
   
    def __init__(self, title, parent, threadLock):

        wx.NotebookPage.__init__(self,parent.getNotebook(),-1)
        self.dataList = []
        self.hiddenDataList = []
        self.tmpDataList = []
        self.tmpHiddenDataList = []
        self.count = 0
        self.selectedRow = 0
        self.title = title
        self.owner = parent
        self.lock = threadLock
        #self.dataListLock = thread.allocate_lock() 
        
        parent.getNotebook().AddPage(self,title)
       
       
        list = self.list = ListCtrlAutoWidth(self)
        list.InsertColumn(0," ",1,20)
        list.InsertColumn(1,u"ユーザ")
        list.InsertColumn(2,u"発言",width=300)
        list.InsertColumn(3,u"時刻",width=60);
        
        # Bind先関数はcontrolに移す
        #list.Bind(wx.EVT_LIST_ITEM_SELECTED,self.OnTwitListSelect)
        #list.Bind(wx.EVT_KEY_DOWN, self.myKeyHandler)
        #list.Bind(wx.EVT_LIST_ITEM_ACTIVATED,self.OnDoubleClick)

        if g_growl == True:
            self.g = parent.g
            self.img = parent.img


class CustomPage(TmpTwitPage):
    """
    カスタムページ(自分でフィルタリングする)
    """
    def __init__(self,title, parent,threadLock):
        TmpTwitPage.__init__(self, title, parent, threadLock)     
        self.dataList = []      


class RecentPage(TmpTwitPage):
    """
    最近のfriendsの発言一覧を表示するページ
    customPageは上に移った
    """
    def __init__(self, parent,threadLock,filter):
		TmpTwitPage.__init__(self,u"最新",parent,threadLock)

		self.customPages = {}# フィルタリングページの固まり？
		self.filter = filter

    
class ReplyPage(TmpTwitPage):

	def __init__(self, parent,threadLock):
		TmpTwitPage.__init__(self,"Re",parent,threadLock)


class DMPage(TmpTwitPage):

	def __init__(self, parent,threadLock):
		TmpTwitPage.__init__(self,"DM",parent,threadLock)
		dataList = []


class TwitHtml(wx.lib.ClickableHtmlWindow.PyClickableHtmlWindow):
	def __init__(self, parent):
		wx.lib.ClickableHtmlWindow.PyClickableHtmlWindow.__init__(self,parent,-1,size=(90,50),style=wx.VSCROLL)

	def SetValue(self, text):
		self.SetPage(text)
		pass


class MainFrame(wx.Frame):
    """
    MainFrame class deffinition.
    """

    TIMER_ID = 1
    TIMER_ID2= TIMER_ID+1
    TIMER_ID3= TIMER_ID2+1
	
    ID_MNU_VIEW_POPUP = 100
    ID_MNU_VIEW_LISTICON = 101
    
    def __init__(self):
        wx.Frame.__init__(self,None, -1, "crochet")

        if g_growl == True:
            self.g = Growl.GrowlNotifier(
                applicationName='crochet',notifications=['newTwit','newReply'])
            self.g.register()
       	    self.img = Growl.Image.imageFromPath('reply.png')	
        self.CreateStatusBar()

        self.selectedRow = -1
        text = self.text = wx.TextCtrl(self,-1,style=wx.TE_PROCESS_ENTER)
        #text.Bind(wx.EVT_TEXT_ENTER, self.OnSendTW)
        button = self.button = wx.Button(self, -1, "Send")
        #self.button.Bind(wx.EVT_BUTTON, self.OnSendTW) 

        notebook = self.notebook = wx.aui.AuiNotebook(
                                       self,
                                       -1,
                                       style= wx.aui.AUI_NB_BOTTOM|
                                              wx.aui.AUI_NB_WINDOWLIST_BUTTON|
                                              wx.aui.AUI_NB_TAB_SPLIT
                                     )
        filter ="" #tmp code
        self.httpThreadLock=""
        self.recentPage = RecentPage(self,self.httpThreadLock,filter)
        self.replyPage = ReplyPage(self,self.httpThreadLock)
        self.directPage = DMPage(self,self.httpThreadLock) 

        """for p in twTabConfig['tabName']:
            page = CustomPage(p,self,self.httpThreadLock)
            self.recentPage.AppendCustomPage(page,p)
        """
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
	
        #self.SetIcon(main_icon.getIcon())
        self.SetSize((600,400))
        
        self.timer = wx.Timer(self,self.TIMER_ID)
        #wx.EVT_TIMER(self,self.TIMER_ID,self.OnUpdate)
        self.timer.Start(60000)
		
        self.timer11 = wx.Timer(self,self.TIMER_ID3+1)
        #wx.EVT_TIMER(self,self.TIMER_ID3+1,self.OnUpdate2)
        self.timer11.Start(3000)

        self.timer2 = wx.Timer(self,self.TIMER_ID2)
        #wx.EVT_TIMER(self,self.TIMER_ID2,self.OnReplyUpdate)
        self.timer2.Start(300000)

        self.timer3 = wx.Timer(self,self.TIMER_ID3)
        #wx.EVT_TIMER(self,self.TIMER_ID3,self.OnDMUpdate)
        self.timer3.Start(300000)

        #self.SetNowTime2StatusBar()
        self.CreateMenu()

    
    def CreateMenu(self):
        #表示メニュー項目作る
        viewMenu = wx.Menu()
        self.popupCheck = viewMenu.Append(self.ID_MNU_VIEW_POPUP,u"新着通知",u"新着表示",kind = wx.ITEM_CHECK)
        self.listIconCheck = viewMenu.Append(self.ID_MNU_VIEW_LISTICON,u"リストアイコン",u"リストボックスの横のアイコンの表示／非表示を切り替えます",kind=wx.ITEM_CHECK)

        g_config = {}
        g_config['popup'] = False #tmp code
        viewMenu.Check(self.ID_MNU_VIEW_POPUP, g_config['popup'])
        menuBar = wx.MenuBar()
        menuBar.Append(viewMenu,u"表示")

        #あとでcontrollerに結びつける
        #wx.EVT_MENU(self, self.ID_MNU_VIEW_POPUP, self.OnMenuViewPopUp_Click)
        #wx.EVT_MENU(self, self.ID_MNU_VIEW_LISTICON, self.OnMenuViewListIcon_Click)
        self.SetMenuBar(menuBar)

    def getNotebook(self):
        return self.notebook

# startup application.
if __name__=='__main__':
    app = wx.App(False)
    frame = MainFrame()
    app.SetTopWindow(frame)
    frame.Show()
    app.MainLoop()
