#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2013-2014  Vincent Paeder
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

    Read scan event class

"""

from terapy.scan.read import ReadBase
from terapy.core.choice import ChoicePopup
import wx

class Read(ReadBase):
    """
    
        Read scan event class
    
    """
    __extname__ = "Read"
    def __init__(self, parent = None):
        ReadBase.__init__(self, parent)
        # Generic read
        self.input = 0
        self.index = 0
        self.propNames = ["Input","Quantity"]
        self.is_input = True
        self.is_visible = True
        self.config = ["input","index"]

    def refresh(self):
        ReadBase.refresh(self)
        if self.index<0:
            self.index=0
        if self.index>=len(self.inlist[self.input].qtynames):
            self.index = len(self.inlist[self.input].qtynames)-1
        
    def run(self, data):
        if self.can_run:
            inp = self.inlist[self.input]
            data.SetCurrentValue(self.m_id, inp.read()[self.index])

    def set(self, parent=None):
        self.refresh()
        dlg = ReadEventDialog(parent, inlist=self.inlist, value=self.input, index=self.index)
        if dlg.ShowModal() == wx.ID_OK:
            self.input, self.index = dlg.GetValue()
            dlg.Destroy()
            return True
        else:
            dlg.Destroy()
            return False

    def edit_label(self, event, pos):
        ReadBase.edit_label(self, event, pos)
        if pos==1:
            event.Veto()
            br = self.host.GetBoundingRect(self.get_property_node(1))
            w = ChoicePopup(self.host,-1,choices=self.inlist[self.input].qtynames,pos=br.GetPosition(), size=br.GetSize(), style=wx.CB_DROPDOWN|wx.CB_READONLY)
            w.SetSelection(self.index)
            w.Bind(wx.EVT_CHOICE,self.onSelectIndex)
            w.SetFocus()
            if wx.Platform == '__WXMSW__':
                w.Bind(wx.EVT_KILL_FOCUS,self.onSelectIndex)

    def onSelectIndex(self, event=None):
        self.index = event.GetEventObject().GetSelection()
        self.propNodes[0] = self.inlist[self.input].name
        self.propNodes[1] = self.inlist[self.input].qtynames[self.index]
        self.set_property_nodes()
        # notify tree that editing is finished
        evt = wx.TreeEvent(wx.wxEVT_COMMAND_TREE_END_LABEL_EDIT,self.host.GetId())
        evt.SetItem(self.host.GetSelection())
        self.host.GetEventHandler().ProcessEvent(evt)
    
    def onSelectInput(self, event=None):
        self.input = event.GetEventObject().GetSelection()
        self.propNodes[0] = self.inlist[self.input].name
        self.refresh()
        self.propNodes[1] = self.inlist[self.input].qtynames[self.index]
        self.set_property_nodes()
        # notify tree that editing is finished
        evt = wx.TreeEvent(wx.wxEVT_COMMAND_TREE_END_LABEL_EDIT,self.host.GetId())
        evt.SetItem(self.host.GetSelection())
        self.host.GetEventHandler().ProcessEvent(evt)
    
    def populate(self):
        self.refresh()
        try:
            self.propNodes = [self.inlist[self.input].name,self.inlist[self.input].qtynames[self.index]]
        except:
            self.propNodes = ["",""]
        self.create_property_root()
        self.set_property_nodes(True)

class ReadEventDialog(wx.Dialog):
    """
    
        Read scan event configuration dialog
    
    """
    def __init__(self, parent = None, title="Select measurement source", inlist = [], value = 0, index = 0):
        """
        
            Initialization.
            
            Parameters:
                parent    -    parent window (wx.Window)
                title     -    dialog title (str)
                inlist    -    input device list (list of devices)
                value     -    default selection (int)
                index     -    default index (int)
        
        """
        wx.Dialog.__init__(self, parent, title=title)
        self.label_input = wx.StaticText(self, -1, "Input source")
        self.choice_input = wx.Choice(self, -1, choices=[x.name for x in inlist])
        self.label_index = wx.StaticText(self, -1, "Quantity")
        self.choice_index = wx.Choice(self, -1, choices=inlist[value].qtynames)
        self.button_OK = wx.Button(self, wx.ID_OK)
        self.button_Cancel = wx.Button(self, wx.ID_CANCEL)
        self.choice_input.SetSelection(value)
        self.choice_index.SetSelection(index)
        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.AddStretchSpacer(1)
        hbox.Add(self.button_Cancel, 0, wx.RIGHT|wx.ALIGN_RIGHT, 5)
        hbox.Add(self.button_OK, 0, wx.RIGHT|wx.ALIGN_RIGHT, 5)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.label_input, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.choice_input, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.label_index, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.choice_index, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(hbox, 0, wx.ALL|wx.EXPAND, 2)
        self.SetSizer(sizer)
        self.Fit()
    
    def GetValue(self):
        """
        
            Return dialog value.
            
            Output:
                selected input device index (int), selected quantity index (int)
        
        """
        return self.choice_input.GetSelection(), self.choice_index.GetSelection()
