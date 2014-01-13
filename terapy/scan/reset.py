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

    Reset device scan event class

"""

from terapy.scan.base import ScanEvent
import wx
from terapy.core.choice import ChoicePopup
from terapy.core import icon_path

class Reset(ScanEvent):
    """
    
        Reset device scan event class
        
        Trigger reset for selected device.
    
    """
    __extname__ = "Reset"
    def __init__(self, parent = None):
        ScanEvent.__init__(self, parent)
        self.instr = 0
        self.instrlist = []
        self.propNames = ["Instrument"]
        self.config = ["instr"]
    
    def refresh(self):
        ScanEvent.refresh(self)
        from terapy.hardware import devices
        self.instrlist = devices['axis']
        self.instrlist.extend(devices['input'])
    
    def run(self, data):
        if self.can_run:
            self.instrlist[self.instr].reset()
        
    def set(self, parent=None):
        self.refresh()
        dlg = InstrumentSelectionDialog(parent, instrlist=[x.name for x in self.instrlist], instr=self.instr)
        if dlg.ShowModal() == wx.ID_OK:
            self.instr = dlg.GetValue()
            dlg.Destroy()
            return True
        else:
            dlg.Destroy()
            return False

    def populate(self):
        self.propNodes = [self.instrlist[self.instr].name]
        self.create_property_root()
        self.set_property_nodes(True)

    def set_property(self, pos, val):
        self.propNodes = [self.instrlist[self.instr].name]
        self.set_property_nodes(True)
        
    def edit_label(self, event, pos):
        if pos==0:
            event.Veto()
            br = self.host.GetBoundingRect(self.get_property_node(0))
            w = ChoicePopup(self.host,-1,choices=[x.name for x in self.instrlist],pos=br.GetPosition(), size=br.GetSize(), style=wx.CB_DROPDOWN|wx.CB_READONLY)
            w.SetSelection(self.instr)
            w.Bind(wx.EVT_CHOICE,self.onSelectInstr)
            if wx.Platform == '__WXMSW__':
                w.Bind(wx.EVT_KILL_FOCUS,self.onSelectInstr)
            else:
                w.Bind(wx.EVT_LEAVE_WINDOW,self.onSelectInstr)
            self.set_property_nodes(True)

    def onSelectInstr(self, event=None):
        self.instr = event.GetEventObject().GetSelection()
        self.propNodes[0] = self.instrlist[self.instr].name
        self.set_property_nodes(True)

    def get_icon(self):
        return wx.Image(icon_path + "event-reset.png").ConvertToBitmap()

class InstrumentSelectionDialog(wx.Dialog):
    """
    
        Reset device scan event configuration dialog
    
    """
    def __init__(self, parent = None, title="Reset instrument", instrlist = [], instr = 0):
        """
        
            Initialization.
            
            Parameters:
                parent    -    parent window (wx.Window)
                title     -    dialog title (str)
                instrlist -    device list (list of str)
                instr     -    default selection (int)
        
        """
        wx.Dialog.__init__(self, parent, title=title)
        self.label_instr = wx.StaticText(self, -1, "Instrument")
        self.choice_instr = wx.Choice(self, -1, choices=instrlist)
        self.button_OK = wx.Button(self, wx.ID_OK)
        self.button_Cancel = wx.Button(self, wx.ID_CANCEL)
        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.AddStretchSpacer(1)
        hbox.Add(self.button_Cancel, 0, wx.RIGHT|wx.ALIGN_RIGHT, 5)
        hbox.Add(self.button_OK, 0, wx.RIGHT|wx.ALIGN_RIGHT, 5)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.label_instr, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.choice_instr, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(hbox, 0, wx.ALL|wx.EXPAND, 2)
        self.SetSizer(sizer)
        self.Fit()
        self.choice_instr.SetSelection(instr)
    
    def GetValue(self):
        """
        
            Return dialog value.
            
            Output:
                index of selected device (int)
        
        """
        return self.choice_instr.GetSelection()
    