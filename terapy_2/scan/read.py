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

    Read scan event base class

"""

from terapy.scan.base import ScanEvent
import wx
from terapy.core.choice import ChoicePopup
from terapy.core import icon_path

class ReadBase(ScanEvent):
    """
    
        Read scan event base class
    
    """
    __extname__ = "Read"
    def __init__(self, parent = None):
        ScanEvent.__init__(self, parent)
        # Generic read
        self.input = 0
        self.propNames = ["Input"]
        self.is_input = True
        self.is_visible = False
        self.config = ["input"]

    def refresh(self):
        ScanEvent.refresh(self)
        from terapy.hardware import devices
        self.inlist = devices['input']
        if self.input>=len(self.inlist): self.input = len(self.inlist)-1
        if self.input<0: self.input = 0
        
    def run(self, data):
        pass

    def set(self, parent=None):
        self.refresh()
        dlg = InputSelectionDialog(parent, inlist=[x.name for x in self.inlist], value=self.input)
        if dlg.ShowModal() == wx.ID_OK:
            self.input = dlg.GetValue()
            dlg.Destroy()
            return True
        else:
            dlg.Destroy()
            return False
    
    def populate(self):
        self.refresh()
        try:
            self.propNodes = [self.inlist[self.input].name]
        except:
            self.propNodes = [""]
        self.create_property_root()
        self.set_property_nodes(True)

    def edit_label(self, event, pos):
        self.refresh()
        if pos==0:
            event.Veto()
            br = self.host.GetBoundingRect(self.get_property_node(0))
            w = ChoicePopup(self.host,-1,choices=[x.name for x in self.inlist],pos=br.GetPosition(), size=br.GetSize(), style=wx.CB_DROPDOWN|wx.CB_READONLY)
            w.SetSelection(self.input)
            w.Bind(wx.EVT_CHOICE,self.onSelectInput)
            w.SetFocus()
            if wx.Platform == '__WXMSW__':
                w.Bind(wx.EVT_KILL_FOCUS,self.onSelectInput)

    def onSelectInput(self, event=None):
        self.input = event.GetEventObject().GetSelection()
        self.propNodes[0] = self.inlist[self.input].name
        self.set_property_nodes()
        # notify tree that editing is finished
        evt = wx.TreeEvent(wx.wxEVT_COMMAND_TREE_END_LABEL_EDIT,self.host.GetId())
        evt.SetItem(self.host.GetSelection())
        self.host.GetEventHandler().ProcessEvent(evt)

    def get_icon(self):
        return wx.Image(icon_path + "event-read.png").ConvertToBitmap()

class InputSelectionDialog(wx.Dialog):
    """
    
        Read scan event configuration dialog
    
    """
    def __init__(self, parent = None, title="Select input", inlist = [], value = 0):
        """
        
            Initialization.
            
            Parameters:
                parent    -    parent window (wx.Window)
                title     -    dialog title (str)
                inlist    -    input device list (list of str)
                value     -    default selection (int)
        
        """
        wx.Dialog.__init__(self, parent, title=title)
        self.label_input = wx.StaticText(self, -1, "Input")
        self.choice_input = wx.Choice(self, -1, choices=inlist)
        self.button_OK = wx.Button(self, wx.ID_OK)
        self.button_Cancel = wx.Button(self, wx.ID_CANCEL)
        self.choice_input.SetSelection(value)
        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.AddStretchSpacer(1)
        hbox.Add(self.button_Cancel, 0, wx.RIGHT|wx.ALIGN_RIGHT, 5)
        hbox.Add(self.button_OK, 0, wx.RIGHT|wx.ALIGN_RIGHT, 5)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.label_input, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.choice_input, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(hbox, 0, wx.ALL|wx.EXPAND, 2)
        self.SetSizer(sizer)
        self.Fit()
    
    def GetValue(self):
        """
        
            Return dialog value.
            
            Output:
                selected input device index (int)
        
        """
        return self.choice_input.GetSelection()
