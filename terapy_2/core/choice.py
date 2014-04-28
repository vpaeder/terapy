#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2013  Vincent Paeder
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""

    Choice widget

"""

import wx.combo
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin 

class ListViewComboPopup(wx.ListCtrl, wx.combo.ComboPopup, ListCtrlAutoWidthMixin):
    """
    
        ListView combo popup
    
    """
    def __init__(self, *args, **kwds):
        self.PostCreate(wx.PreListCtrl())
        wx.combo.ComboPopup.__init__(self, *args, **kwds)
        
    def Create(self, parent):
        wx.ListCtrl.Create(self, parent, -1, (0,0), wx.DefaultSize, style=wx.LC_REPORT|wx.LC_NO_HEADER|wx.LC_SINGLE_SEL)
        ListCtrlAutoWidthMixin.__init__(self) # add auto width support
        self.setResizeColumn(0)
        self.Bind(wx.EVT_MOTION, self.OnMotion)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        return True
        
    def Init(self):
        self.value = -1
        self.curitem = -1

    def GetControl(self):
        return self
    
    def GetSelection(self):
        return self.curitem
    
    def OnDismiss(self):
        evt = wx.PyCommandEvent(wx.wxEVT_COMMAND_CHOICE_SELECTED,self.GetId())
        evt.EventObject = self.GetCombo()
        self.GetEventHandler().ProcessEvent(evt)
        wx.combo.ComboPopup.OnDismiss(self)
    
    def OnPopup(self):
        wx.combo.ComboPopup.OnPopup(self)
    
    def OnMotion(self, evt):
        item, flags = self.HitTest(evt.GetPosition())
        if item >= 0:
            self.Select(item)
            self.curitem = item
    
    def OnLeftDown(self, evt):
        self.value = self.curitem
        self.GetCombo().value = self.value
        self.GetCombo().SetValueWithEvent(self.GetCombo().choices[self.value])
        self.Dismiss()

class ChoicePopup(wx.combo.ComboCtrl):
    """
    
        Implement choice widget, which unfolds programmatically
      
    """
    def __init__(self,parent, id=wx.ID_ANY, value="", choices=[], pos=wx.DefaultPosition, size=wx.DefaultSize, style=0, validator=wx.DefaultValidator, name=""):
        wx.combo.ComboCtrl.__init__(self, parent, id, value, pos, size, style, validator, name)
        self.list = ListViewComboPopup()
        self.SetPopupControl(self.list)
        self.list.InsertColumn(0,"")
        self.choices = choices
        self.value = 0
        for n in range(len(choices)):
            self.list.InsertStringItem(n,choices[n])
        height = 0
        for n in range(len(choices)):
            height += self.list.GetItemRect(n).GetSize()[1]
        self.list.SetMaxSize((-1,height+2))
        self.list.SetMinSize((-1,height+2))
        self.list.SetSize((-1,height+2))
        self.deleted = False
        
        self.ShowPopup()
    
    def DestroyPopup(self):
        self.list.Destroy()
    
    def SetSelection(self, pos):
        if pos>len(self.choices)-1: pos = len(self.choices)-1
        if pos<0: pos=0 
        self.SetValue(self.choices[pos])
        self.value = pos
        self.list.Select(pos)

    def GetSelection(self):
        if not(self.deleted): # need this dirty trick to avoid calling Destroy twice
            wx.CallAfter(self.Destroy)
            self.deleted = True
        return self.value
