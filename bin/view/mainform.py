#!/usr/bin/env python
#! -*- coding:utf-8 -*-

import model	
from time import localtime, strftime
from cStringIO import StringIO
import wx.aui
class MainFrame(wx.Frame):
	"""MainFrame class deffinition.
	"""
	#binder = wx_utils.bind_manager()

	TIMER_ID = 1
	TIMER_ID2= TIMER_ID+1
	TIMER_ID3= TIMER_ID2+1
	
	ID_MNU_VIEW_POPUP = 100
	ID_MNU_VIEW_LISTICON = 101
	imageList = model.ImageList() 
	t = {}
	def loadUserData(self, fileName):
		#ファイルを開いて、データを読み込んで変換する
		#データ形式は(user,password)
		#try
		file = open(fileName,'r')
		a = simplejson.loads(file.read())
		file.close()
		return a
		#catch exit(1)
		
	def __init__(self, parent=None, controller=None):
		#from pit import Pit
		#twUserdata = Pit.get('twitter.com',{'require' : {'user':'','pass':''}})
		try:
			twUserdata = self.loadUserData(".chat/twdata")
		except:
			twUserdata = config.ConfigDialog(None, -1, 'crochet config').GetAccount()
			if twUserdata["user"] and twUserdata["pass"]:
				file = open(".chat/twdata","w")
				file.write("{\"user\":\""+twUserdata["user"]+
					   "\",\"pass\":\""+twUserdata["pass"]+"\"}\n")
				file.close()
			else:
				exit(1)
		twTabConfig = self.loadUserData(".chat/tabconfig")

		wx.Frame.__init__(self,None, -1, "crochet")
		

		if g_growl == True:
			self.g = Growl.GrowlNotifier(
				applicationName='crochet',notifications=['newTwit','newReply'])
			self.g.register()
			self.img = Growl.Image.imageFromPath('reply.png')	
		self.CreateStatusBar()

		self.selectedRow = -1
		text = self.text = wx.TextCtrl(self,-1,style=wx.TE_PROCESS_ENTER)
		text.Bind(wx.EVT_TEXT_ENTER, controller.OnSendTW)
		button = self.button = wx.Button(self, -1, "Send")
		self.button.Bind(wx.EVT_BUTTON, controller.OnSendTW) 
	
		notebook = self.notebook = wx.aui.AuiNotebook(self,-1,style=wx.aui.AUI_NB_BOTTOM|wx.aui.AUI_NB_WINDOWLIST_BUTTON|wx.aui.AUI_NB_TAB_SPLIT)

		self.imageThreadLock = thread.allocate_lock()
		self.httpThreadLock = thread.allocate_lock()
		self.dataListThreadLock = thread.allocate_lock()	
		filter = []
		for f in twTabConfig['tabFilter']:
			filter.append(BranchFilter(f[0],f[1],f[2],f[3],f[4],f[5],f[6])	)	
		
		self.recentPage = RecentPage(self,self.httpThreadLock,filter)
		self.replyPage = ReplyPage(self,self.httpThreadLock)
		self.directPage = DMPage(self,self.httpThreadLock) 

		for p in twTabConfig['tabName']:
			page = CustomPage(p,self,self.httpThreadLock)
			self.recentPage.AppendCustomPage(page,p)	
		
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
	
		self.tw = twitter3.Twitter(twUserdata)
		self.tw.setAuthService("twitter")
		self.SetIcon(main_icon.getIcon())
		self.SetSize((300,400))
		self.timer = wx.Timer(self,self.TIMER_ID)
		wx.EVT_TIMER(self,self.TIMER_ID,self.OnUpdate)
		self.timer.Start(60000)
		
		self.timer11 = wx.Timer(self,self.TIMER_ID3+1)
		wx.EVT_TIMER(self,self.TIMER_ID3+1,self.OnUpdate2)
		self.timer11.Start(3000)

		self.timer2 = wx.Timer(self,self.TIMER_ID2)
		wx.EVT_TIMER(self,self.TIMER_ID2,self.OnReplyUpdate)
		self.timer2.Start(300000)
		
		self.timer3 = wx.Timer(self,self.TIMER_ID3)
		wx.EVT_TIMER(self,self.TIMER_ID3,self.OnDMUpdate)
		self.timer3.Start(300000)
		
		self.RefreshTw()
		self.replyPage.Refresh()
		self.directPage.Refresh()

		self.SetNowTime2StatusBar()
		self.CreateMenu()	
	def CreateMenu(self):
		#表示メニュー項目作る
		viewMenu = wx.Menu()
		self.popupCheck = viewMenu.Append(self.ID_MNU_VIEW_POPUP,u"新着通知",u"新着表示",kind = wx.ITEM_CHECK)
		self.listIconCheck = viewMenu.Append(self.ID_MNU_VIEW_LISTICON,u"リストアイコン",u"リストボックスの横のアイコンの表示／非表示を切り替えます",kind=wx.ITEM_CHECK)

		viewMenu.Check(self.ID_MNU_VIEW_POPUP, g_config['popup'])
		menuBar = wx.MenuBar()
		menuBar.Append(viewMenu,u"表示")

		wx.EVT_MENU(self, self.ID_MNU_VIEW_POPUP, self.OnMenuViewPopUp_Click)
		wx.EVT_MENU(self, self.ID_MNU_VIEW_LISTICON, self.OnMenuViewListIcon_Click)
		self.SetMenuBar(menuBar)

	def OnMenuViewPopUp_Click(self,e):
		g_config['popup'] = self.popupCheck.IsChecked();

	def OnMenuViewListIcon_Click(self,e):
		g_config['listIcon'] = self.listIconCheck.IsChecked();

	def OnSendTW(self, event):
		# 送信する
		# コンボボックスの中身を空にする
		combo =	self.text 
		self.tw.put(combo.GetValue())	
		combo.SetValue("")
		self.RefreshTw()
	
	# チャットのログデータをListCtrlに表示
	def RefreshTw(self):
		self.recentPage.Refresh()	
	
	def OnUpdate(self, event):
		self.SetStatusBar(u"新着取得中...")
		self.RefreshTw()
	
	def OnUpdate2(self, event):
		#self.SetStatusBar(u"新着取得中...")
		b1 = self.recentPage.CheckUpdate()
		for c in self.recentPage.customPages:
			b2 = self.recentPage.customPages[c].CheckUpdate()
		self.replyPage.CheckUpdate()
		self.directPage.CheckUpdate()
		if b1 == True:
			self.SetNowTime2StatusBar()

	def OnReplyUpdate(self, event):
			
		self.SetStatusBar(u"Reply取得中")
		self.replyPage.Refresh()

	def OnDMUpdate(self, event):
		
		self.SetStatusBar(u"DM取得中...")
		self.directPage.Refresh()

	def SetStatusBar(self,str):
		#print ("setstatusbar"+str,)	
		sb = wx.GetApp().GetTopWindow().GetStatusBar()
		sb.SetStatusText(str)

	def SetNowTime2StatusBar(self):
		#現在時刻を表示

		nowtime = strftime("%H:%M:%S", localtime())
		sb = wx.GetApp().GetTopWindow().GetStatusBar()
		sb.SetStatusText(nowtime+u"に更新しました")
	
	def myKeyHandler(self,evt):
		print evt.GetKeyCode(), 
		if self.selectedRow != -1:
			if evt.GetKeyCode() in [ord('k'),ord('K'),wx.WXK_UP]:
				print ('up')
				if self.selectedRow > 0:
		 			self.MoveList(self.selectedRow-1)
			if evt.GetKeyCode() in [ord('j'),ord('J'),wx.WXK_DOWN]:
				print ('down')
				if self.selectedRow < self.list.GetItemCount()-1:
					self.MoveList(self.selectedRow+1)
			if evt.GetKeyCode() in [ord('h'),ord('H'),wx.WXK_LEFT]:
				print ('left')
				leftcol = self.GetPrevItem(self.selectedRow)
				if leftcol != -1:
					self.MoveList(leftcol)
			if evt.GetKeyCode() in [ord('l'),ord('L'),wx.WXK_RIGHT]:
				print ('right')	
				rightcol = self.GetNextItem(self.selectedRow)
				if rightcol != -1:
					self.MoveList(rightcol)
			if evt.GetKeyCode() in [ord('s'),ord('S')]:
				print "S"
				#id = self.hiddenDataList[self.selectedRow][0]
				#print "fav"+id
				#self.tw.createFavorite(id)
		#print list.
		if evt.GetKeyCode() in [ord('q'), ord('Q')]:
			wx.Exit()

	"""Web上の画像を読み込みImageListとして保持する。
	   	既に読まれてるなら読みに行かない。ImageList['URL']という形で格納
	"""
	def GetImageListElement(self,url):
		unicodeUrl = url
		if self.imageList.has_key(unicodeUrl):
			if self.imageList[unicodeUrl] == "":
				return None 
			return self.imageList[unicodeUrl]
		else:
			self.imageList[unicodeUrl] = "" 
			self.WebImage2StringIO(url,unicodeUrl)
		return None 
	
	# Web上の画像を引っ張ってくる
	def WebImage2StringIO(self,url,result):

		try:
			urlName = urllib.quote_plus(url,':;/')
			t = ImageGetFrame(urlName,self.WebImageCallback,result,self.imageThreadLock)
			t.start()
			#t.run()
		except:
			print "urlquote error"
			#print "urlName:"+urlName

	def WebImageCallback(self,imageData,result):
		image_pil = Image.open(StringIO(imageData))
		image_pil.thumbnail((64,64))

		image_wx = wx.EmptyImage(image_pil.size[0],image_pil.size[1])
		image_wx.SetData(image_pil.convert('RGB').tostring())
		self.imageList[result] = image_wx
	
	# 画像を読み込んで表示のテスト
	def SetImage(self,imageName):
		bmp = self.userIcon
		image = self.GetImageListElement(imageName)
		if image != None: 
			bmp.SetBitmap(image.ConvertToBitmap())
	
	def addUser2Inputbox(self,user):
		
		text = self.text
		value = text.GetValue()
		
		flag = 1 
		print value + ":" + user
		if re.search(user,value):
			flag = 0

		if flag == 1:
			text.SetValue(user+value)

	def getNotebook(self):
		return self.notebook
