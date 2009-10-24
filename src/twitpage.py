#!/usr/bin/env python
# -*- coding: utf-8 -*-
import wx
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin

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
        wx.NotebookPage.__init__(self, parent.get_notebook(), -1)
        
        parent.get_notebook().AddPage(self,title)
        
        list = self.list = ListCtrlAutoWidth(self)
        #list.Bind(wx.EVT_KEY_DOWN, self.myKeyHandler)
        #list.Bind(wx.EVT_LIST_ITEM_ACTIVATED,self.OnDoubleClick)
        
        list.InsertColumn(0, " ", 1, 20)
        list.InsertColumn(1, u"ユーザ")
        list.InsertColumn(2, u"発言", width=300)
        list.InsertColumn(3, u"時刻", width=60);
        #list.Bind(wx.EVT_LIST_ITEM_SELECTED,self.OnTwitListSelect)

        #a = self.imageListProxy = ImageListProxy()
        #list.AssignImageList( a.imageList, wx.IMAGE_LIST_SMALL)
    
    def update(self, data):
        """リスト更新時に呼ばれる
        派生クラスで実装する
        """
        pass

class RecentPage(TmpTwitPage):
    """
    最近のfriendsの発言一覧を表示するページ
    """
    def __init__(self, parent,filter):
        TmpTwitPage.__init__(self,u"最新",parent)
        
    def update(self, data):
        i = 0
        for x in data:
            flag = 0
            # 重複発言チェック            
            """for d in self.dataList:
                if d["user"] == x["user"]:
                    flag = 1
                    break
            """

            """for p in self.customPages:
                for d in self.customPages[p].dataList:
                    if d[2] == x[1]:
                        flag = 1
                        break
                if flag == 1: break    
            """
            if flag == 1: break
            
            x2 = "--"
            list_data = ("", x["user"], x["text"], x2)
            self.list.InsertStringItem(i,"")
            for j in range(len(list_data)):
                self.list.SetStringItem(i, j, list_data[j])
            i += 1    
