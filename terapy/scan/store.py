#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2014  Vincent Paeder
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

    Move axis device scan event class

"""

from terapy.scan.base import ScanEvent
import wx
from terapy.core.choice import ChoicePopup
from terapy.core import icon_path
from terapy.hardware.axes import AxisDevice
from terapy.core import store

class Store(ScanEvent):
    """
    
        Store scan event class
        
        Store value of given device for later use.
    
    """
    __extname__ = "Store"
    def __init__(self, parent = None):
        ScanEvent.__init__(self, parent)
        self.instr = 0
        self.instrlist = []
        self.quantity = 0
        self.tag = "tmp"
        self.propNames = ["Instrument","Quantity","Tag"]
        self.config = ["instr","quantity","tag"]
    
    def refresh(self):
        ScanEvent.refresh(self)
        from terapy.hardware import devices
        self.instrlist = devices['axis'][:]
        self.instrlist.extend(devices['input'][:])
        if self.instr>=len(self.instrlist):
            self.instr = len(self.instrlist)-1
        
        if isinstance(self.instrlist[self.instr],AxisDevice):
            self.quantity = 0
        else:
            if self.quantity>=len(self.instrlist[self.instr].qtynames):
                self.quantity = len(self.instrlist[self.instr].qtynames)-1
    
    def run(self, data):
        if self.can_run:
            if isinstance(self.instrlist[self.instr],AxisDevice):
                store.Save(self.instrlist[self.instr].pos(), self.tag)
            else:
                store.Save(self.instrlist[self.instr].read()[self.quantity], self.tag)
        
    def set(self, parent=None):
        self.refresh()
        dlg = StoreEventDialog(parent, instrlist=self.instrlist, instr=self.instr, quantity=self.quantity, tag=self.tag)
        if dlg.ShowModal() == wx.ID_OK:
            self.instr,self.quantity,self.tag = dlg.GetValue()
            dlg.Destroy()
            return True
        else:
            dlg.Destroy()
            return False

    def set_nodes(self):
        self.propNodes = [self.instrlist[self.instr].name, "", self.tag]
        if isinstance(self.instrlist[self.instr],AxisDevice):
            self.propNodes[1] = self.instrlist[self.instr].qtynames
        else:
            self.propNodes[1] = self.instrlist[self.instr].qtynames[self.quantity]
    
    def populate(self):
        self.set_nodes()
        self.create_property_root()
        self.set_property_nodes(True)
    
    def set_property(self, pos, val):
        try:
            if pos==1:
                self.position = float(val)
        except:
            pass
        self.set_nodes()
        self.set_property_nodes(True)
        
    def edit_label(self, event, pos):
        if pos==0:
            event.Veto()
            br = self.host.GetBoundingRect(self.get_property_node(0))
            w = ChoicePopup(self.host,-1,choices=[x.name for x in self.instrlist],pos=br.GetPosition(), size=br.GetSize(), style=wx.CB_DROPDOWN|wx.CB_READONLY)
            w.SetSelection(self.instr)
            w.Bind(wx.EVT_CHOICE,self.onSelectInstrument)
            if wx.Platform == '__WXMSW__':
                w.Bind(wx.EVT_KILL_FOCUS,self.onSelectInstrument)
            #else:
            #    w.Bind(wx.EVT_LEAVE_WINDOW,self.onSelectAxis)
            self.set_property_nodes(True)
        elif pos==1:
            event.Veto()
            br = self.host.GetBoundingRect(self.get_property_node(0))
            if isinstance(self.instrlist[self.instr],AxisDevice):
                w = ChoicePopup(self.host,-1,choices=[self.instrlist[self.instr].qtynames],pos=br.GetPosition(), size=br.GetSize(), style=wx.CB_DROPDOWN|wx.CB_READONLY)
            else:
                w = ChoicePopup(self.host,-1,choices=self.instrlist[self.instr].qtynames,pos=br.GetPosition(), size=br.GetSize(), style=wx.CB_DROPDOWN|wx.CB_READONLY)
            w.SetSelection(self.quantity)
            w.Bind(wx.EVT_CHOICE,self.onSelectQuantity)
            if wx.Platform == '__WXMSW__':
                w.Bind(wx.EVT_KILL_FOCUS,self.onSelectQuantity)
            self.set_property_nodes(True)
    
    def onSelectInstrument(self, event=None):
        self.instr = event.GetEventObject().GetSelection()
        self.refresh()
        self.set_nodes()
        self.set_property_nodes(True)
        # notify tree that editing is finished
        evt = wx.TreeEvent(wx.wxEVT_COMMAND_TREE_END_LABEL_EDIT,self.host.GetId())
        evt.SetItem(self.host.GetSelection())
        self.host.GetEventHandler().ProcessEvent(evt)
    
    def onSelectQuantity(self, event=None):
        self.quantity = event.GetEventObject().GetSelection()
        self.refresh()
        self.set_nodes()
        self.set_property_nodes(True)
        # notify tree that editing is finished
        evt = wx.TreeEvent(wx.wxEVT_COMMAND_TREE_END_LABEL_EDIT,self.host.GetId())
        evt.SetItem(self.host.GetSelection())
        self.host.GetEventHandler().ProcessEvent(evt)

    def get_icon(self):
        return wx.Image(icon_path + "event-store.png").ConvertToBitmap()

class StoreEventDialog(wx.Dialog):
    """
    
        Read scan event configuration dialog
    
    """
    def __init__(self, parent = None, title="Select measurement source", instrlist = [], instr = 0, quantity = 0, tag = "tmp"):
        """
        
            Initialization.
            
            Parameters:
                parent    -    parent window (wx.Window)
                title     -    dialog title (str)
                instrlist -    input device list (list of devices)
                instr     -    default selection (int)
                quantity  -    default index (int)
                tag       -    storage name (str)
        
        """
        wx.Dialog.__init__(self, parent, title=title)
        self.label_input = wx.StaticText(self, -1, "Input source")
        self.choice_input = wx.Choice(self, -1, choices=[x.name for x in instrlist])
        self.label_quantity = wx.StaticText(self, -1, "Quantity")
        self.choice_quantity = wx.Choice(self, -1, choices=[])
        self.label_tag = wx.StaticText(self, -1, "Tag name")
        self.input_tag = wx.TextCtrl(self, -1, tag)
        self.button_OK = wx.Button(self, wx.ID_OK)
        self.button_Cancel = wx.Button(self, wx.ID_CANCEL)
        self.choice_input.SetSelection(instr)
        self.Bind(wx.EVT_CHOICE, self.OnInputSelect, self.choice_input)
        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.AddStretchSpacer(1)
        hbox.Add(self.button_Cancel, 0, wx.RIGHT|wx.ALIGN_RIGHT, 5)
        hbox.Add(self.button_OK, 0, wx.RIGHT|wx.ALIGN_RIGHT, 5)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.label_input, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.choice_input, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.label_quantity, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.choice_quantity, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.label_tag, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.input_tag, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(hbox, 0, wx.ALL|wx.EXPAND, 2)
        self.SetSizer(sizer)
        self.Fit()
        
        self.instrlist = instrlist
        self.quantity = quantity
    
        self.Bind(wx.EVT_BUTTON, self.OnOkButton, self.button_OK)
        self.Bind(wx.EVT_BUTTON, self.OnCancelButton, self.button_Cancel)
        self.OnInputSelect()
    
    def OnOkButton(self, event=None):
        wx.CallAfter(self.EndModal,wx.ID_OK)

    def OnCancelButton(self, event=None):
        wx.CallAfter(self.EndModal,wx.ID_CANCEL)

    def OnInputSelect(self, event=None):
        """
        
            Actions following change of input device.
        
        """
        input = self.choice_input.GetSelection()
        if event!=None:
            self.quantity = self.choice_quantity.GetSelection()
        
        self.choice_quantity.Clear()
        
        if isinstance(self.instrlist[input], AxisDevice):
            qtynames = [self.instrlist[input].qtynames]
        else:
            qtynames = self.instrlist[input].qtynames
            
        self.choice_quantity.AppendItems(qtynames)
        
        if self.quantity>=len(qtynames): self.quantity = len(qtynames)-1 
        self.choice_quantity.SetSelection(self.quantity)

    def GetValue(self):
        """
        
            Return dialog value.
            
            Output:
                selected input device index (int), selected quantity index (int)
        
        """
        return self.choice_input.GetSelection(), self.choice_quantity.GetSelection(), self.input_tag.GetValue()
