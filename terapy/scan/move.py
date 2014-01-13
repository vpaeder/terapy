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

    Move axis device scan event class

"""

from terapy.scan.base import ScanEvent
import wx
from time import sleep
from terapy.core.choice import ChoicePopup
from terapy.core import icon_path

class Move(ScanEvent):
    """
    
        Move axis device scan event class
        
        Move selected axis device to given position.
    
    """
    __extname__ = "Move"
    def __init__(self, parent = None):
        ScanEvent.__init__(self, parent)
        self.axis = 0
        self.axlist = []
        self.position = 0.0
        self.relative = False
        self.propNames = ["Axis","Position","Relative"]
        self.config = ["axis","position","relative"]
        self.is_axis = True
    
    def refresh(self):
        ScanEvent.refresh(self)
        from terapy.hardware import devices
        self.axlist = devices['axis']
        if self.axis>=len(self.axlist): self.axis = len(self.axlist)-1
        if self.axis<0: self.axis = 0

    def run(self, data):
        if self.can_run:
            ax = self.axlist[self.axis]
            if self.relative:
                p0 = ax.pos()
            else:
                p0 = 0
            ax.goTo(p0+self.position)
            while (ax.get_motion_status() != 0 and self.can_run):
                sleep(0.01)
        
    def set(self, parent=None):
        self.refresh()
        dlg = AxisSelectionDialog(parent, axlist=[x.name for x in self.axlist], axis=self.axis, position=self.position, relative=self.relative)
        if dlg.ShowModal() == wx.ID_OK:
            self.axis,self.position,self.relative = dlg.GetValue()
            dlg.Destroy()
            return True
        else:
            dlg.Destroy()
            return False

    def populate(self):
        self.propNodes = [self.axlist[self.axis].name, self.position, ["No","Yes"][self.relative]]
        self.propNames[1] = ["Position","Displacement"][self.relative]
        self.create_property_root()
        self.set_property_nodes(True)

    def set_property(self, pos, val):
        try:
            if pos==1:
                self.position = float(val)
        except:
            pass
        self.propNodes = [self.axlist[self.axis].name, self.position, ["No","Yes"][self.relative]]
        self.set_property_nodes(True)
        
    def edit_label(self, event, pos):
        if pos==0:
            event.Veto()
            br = self.host.GetBoundingRect(self.get_property_node(0))
            w = ChoicePopup(self.host,-1,choices=[x.name for x in self.axlist],pos=br.GetPosition(), size=br.GetSize(), style=wx.CB_DROPDOWN|wx.CB_READONLY)
            w.SetSelection(self.axis)
            w.Bind(wx.EVT_CHOICE,self.onSelectAxis)
            if wx.Platform == '__WXMSW__':
                w.Bind(wx.EVT_KILL_FOCUS,self.onSelectAxis)
            #else:
            #    w.Bind(wx.EVT_LEAVE_WINDOW,self.onSelectAxis)
            self.set_property_nodes(True)
        elif pos==2:
            event.Veto()
            self.relative = not(self.relative)
            self.propNodes[2] = ["No","Yes"][self.relative]
            self.propNames[1] = ["Position","Displacement"][self.relative]
            self.set_property_nodes(True)

    def onSelectAxis(self, event=None):
        self.axis = event.GetEventObject().GetSelection()
        self.propNodes[0] = self.axlist[self.axis].name
        self.set_property_nodes(True)
        # notify tree that editing is finished
        evt = wx.TreeEvent(wx.wxEVT_COMMAND_TREE_END_LABEL_EDIT,self.host.GetId())
        evt.SetItem(self.host.GetSelection())
        self.host.GetEventHandler().ProcessEvent(evt)

    def get_icon(self):
        return wx.Image(icon_path + "event-move.png").ConvertToBitmap()

class AxisSelectionDialog(wx.Dialog):
    """
    
        Move axis device scan event configuration dialog
    
    """
    def __init__(self, parent = None, title="Move axis device", axlist = [], axis = 0, position = 0.0, relative = False):
        """
        
            Initialization.
            
            Parameters:
                parent    -    parent window (wx.Window)
                title     -    dialog title (str)
                axlist    -    list of axis devices (list of str)
                axis      -    default selection (int)
                position  -    position (float)
                relative  -    if True, move is relative, absolute if False
        
        """
        wx.Dialog.__init__(self, parent, title=title)
        self.label_axis = wx.StaticText(self, -1, "Axis")
        self.choice_axis = wx.Choice(self, -1, choices=axlist)
        self.label_position = wx.StaticText(self, -1, ["Position:","Displacement:"][relative])
        self.input_position = wx.TextCtrl(self, -1, str(position))
        self.check_relative = wx.CheckBox(self, -1, "Relative move")
        self.button_OK = wx.Button(self, wx.ID_OK)
        self.button_Cancel = wx.Button(self, wx.ID_CANCEL)
        
        self.choice_axis.SetSelection(axis)
        self.check_relative.SetValue(relative)
        self.Bind(wx.EVT_CHECKBOX, self.OnRelativeSelect, self.check_relative)
        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.AddStretchSpacer(1)
        hbox.Add(self.button_Cancel, 0, wx.RIGHT|wx.ALIGN_RIGHT, 5)
        hbox.Add(self.button_OK, 0, wx.RIGHT|wx.ALIGN_RIGHT, 5)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.label_axis, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.choice_axis, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.label_position, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.input_position, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.check_relative, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(hbox, 0, wx.ALL|wx.EXPAND, 2)
        self.SetSizer(sizer)
        self.Fit()
    
    def OnRelativeSelect(self, event=None):
        """
        
            Actions triggered by relative/absolute checkbox ticking.
        
        """
        self.label_position.SetLabel(["Position:","Displacement:"][event.Selection])
    
    def GetValue(self):
        """
        
            Return dialog values.
            
            Output:
                selected axis device index (int), position (float), absolute/relative move (bool)
        
        """
        return self.choice_axis.GetSelection(), float(self.input_position.GetValue()), self.check_relative.GetValue()
