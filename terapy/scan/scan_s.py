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

    Linear straight scan event class

"""

from terapy.scan.base import ScanEvent
import wx
from numpy import linspace, prod
from time import sleep
from terapy.core.choice import ChoicePopup
from terapy.core import icon_path

class Scan(ScanEvent):
    """
    
        Linear straight scan event class
        
        Scan given axis device between two values in a given number of steps.
    
    """
    __extname__ = "Straight scan"
    def __init__(self, parent = None):
        ScanEvent.__init__(self, parent)
        self.axis = 0
        self.min = 0.0
        self.max = 25.6
        self.N = 257
        self.dv = 0.1
        self.propNames = ["Axis","Minimum","Maximum","# Steps","Step"]
        self.is_loop = True
        self.config = ["axis","N","min","max","dv"]
    
    def refresh(self):
        ScanEvent.refresh(self)
        from terapy.hardware import devices
        self.axlist = devices['axis']
        if self.axis>=len(self.axlist): self.axis = len(self.axlist)-1
        if self.axis<0: self.axis = 0
        
    def run(self, data):
        self.itmList = self.get_children()
        ax = self.axlist[self.axis]
        ax.prepareScan()
        # scan selected axis from min to max
        coords = linspace(self.min,self.max,self.N)
        n=-1
        while self.can_run and n<self.N-1:
            n+=1
            ax.goTo(coords[n])
            
            while (ax.get_motion_status() != 0 and self.can_run):
                sleep(0.01)
            
            data.SetCoordinateValue(self.m_ids, ax.pos()) # read axis position
            
            self.run_children(data)
            data.Increment(self.m_ids)

        data.DecrementScanDimension(self.m_ids)
        data.Decrement(self.m_ids)
        return True

    def get_operation_count(self):
        return self.N

    def set(self, parent=None):
        self.refresh()
        dlg = LoopSettingsDialog(parent, axlist=[x.name for x in self.axlist], axis=self.axis, vmin=self.min, vmax=self.max, N=self.N, dv=self.dv)
        if dlg.ShowModal() == wx.ID_OK:
            self.axis,self.min,self.max,self.N,self.dv = dlg.GetValue()
            dlg.Destroy()
            return True
        else:
            dlg.Destroy()
            return False
    
    def populate(self):
        try:
            self.propNodes = [self.axlist[self.axis].name, self.min, self.max, self.N, self.dv]
        except:
            self.propNodes = ["", self.min, self.max, self.N, self.dv]
        self.create_property_root()
        self.set_property_nodes(True)

    def set_property(self, pos, val):
        try:
            if pos==0:
                self.axis = int(val)
            elif pos==1:
                self.min = float(val)
                if self.max==self.min:
                    self.min = self.max - 1.0
            elif pos==2:
                self.max = float(val)
                if self.max==self.min:
                    self.max = self.min + 1.0
            elif pos==3:
                self.N = int(val)
                if self.N<1:
                    self.N = 1
            elif pos==4 and val!=0:
                self.dv = float(val)
                self.N = int((self.max-self.min)/self.dv)+1
            self.dv = (self.max-self.min)/(self.N-1.0)
        except:
            pass
        self.propNodes = [self.axlist[self.axis].name, self.min, self.max, self.N, self.dv]
        self.set_property_nodes()
        
    def edit_label(self, event, pos):
        self.refresh()
        if pos==0:
            event.Veto()
            br = self.host.GetBoundingRect(self.get_property_node(0))
            w = ChoicePopup(self.host,-1,choices=[x.name for x in self.axlist],pos=br.GetPosition(), size=br.GetSize(), style=wx.CB_DROPDOWN|wx.CB_READONLY)
            w.SetSelection(self.axis)
            w.SetFocus()
            w.Bind(wx.EVT_CHOICE,self.onSelectAxis)
            if wx.Platform == '__WXMSW__':
                w.Bind(wx.EVT_KILL_FOCUS,self.onSelectAxis)
            #else:
            #    w.Bind(wx.EVT_LEAVE_WINDOW,self.onSelectAxis)
    
    def onSelectAxis(self, event=None):
        self.axis = event.GetEventObject().GetSelection()
        self.propNodes[0] = self.axlist[self.axis].name
        self.set_property_nodes()
        # notify tree that editing is finished
        evt = wx.TreeEvent(wx.wxEVT_COMMAND_TREE_END_LABEL_EDIT,self.host.GetId())
        evt.SetItem(self.host.GetSelection())
        self.host.GetEventHandler().ProcessEvent(evt)
    
    def get_icon(self):
        return wx.Image(icon_path + "event-scan.png").ConvertToBitmap()

class LoopSettingsDialog(wx.Dialog):
    """
    
        Loop scan event configuration dialog
    
    """
    def __init__(self, parent = None, title="Loop properties", axlist = [], axis = 0, vmin = 0.0, vmax = 25.6, N=257, dv = 0.1):
        """
        
            Initialization.
            
            Parameters:
                parent    -    parent window (wx.Window)
                title     -    dialog title (str)
                axlist    -    list of axis devices (list of str)
                axis      -    default selection (int)
                vmin      -    start value (float)
                vmax      -    end value (float)
                N         -    number of points (int)
                dv        -    step size between points (float)
        
        """
        wx.Dialog.__init__(self, parent, title=title,style=wx.DEFAULT_DIALOG_STYLE)
        self.label_axis = wx.StaticText(self, -1, "Axis")
        self.choice_axis = wx.Choice(self, -1, choices=axlist)
        self.label_min = wx.StaticText(self, -1, "Minimum:")
        self.input_min = wx.TextCtrl(self, -1, str(vmin), style=wx.TE_PROCESS_ENTER)
        self.label_max = wx.StaticText(self, -1, "Maximum:")
        self.input_max = wx.TextCtrl(self, -1, str(vmax), style=wx.TE_PROCESS_ENTER)
        self.label_N = wx.StaticText(self, -1, "Number of steps:")
        self.input_N = wx.TextCtrl(self, -1, str(N), style=wx.TE_PROCESS_ENTER)
        self.label_dv = wx.StaticText(self, -1, "Step size:")
        self.input_dv = wx.TextCtrl(self, -1, str(dv), style=wx.TE_PROCESS_ENTER)
        self.button_OK = wx.Button(self, wx.ID_OK)
        self.button_Cancel = wx.Button(self, wx.ID_CANCEL)
        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.AddStretchSpacer(1)
        hbox.Add(self.button_Cancel, 0, wx.RIGHT|wx.ALIGN_RIGHT, 5)
        hbox.Add(self.button_OK, 0, wx.RIGHT|wx.ALIGN_RIGHT, 5)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.label_axis, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.choice_axis, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.label_min, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.input_min, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.label_max, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.input_max, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.label_N, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.input_N, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.label_dv, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.input_dv, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(hbox, 0, wx.ALL|wx.EXPAND, 2)
        self.SetSizer(sizer)
        self.Fit()
        self.choice_axis.SetSelection(axis)
        
        self.Bind(wx.EVT_TEXT_ENTER, lambda x: self.OnValueChange(0,x), self.input_min)
        self.Bind(wx.EVT_TEXT_ENTER, lambda x: self.OnValueChange(1,x), self.input_max)
        self.Bind(wx.EVT_TEXT_ENTER, lambda x: self.OnValueChange(2,x), self.input_N)
        self.Bind(wx.EVT_TEXT_ENTER, lambda x: self.OnValueChange(3,x), self.input_dv)
        self.input_min.Bind(wx.EVT_KILL_FOCUS, lambda x: self.OnValueChange(0,x), self.input_min)
        self.input_max.Bind(wx.EVT_KILL_FOCUS, lambda x: self.OnValueChange(1,x), self.input_max)
        self.input_N.Bind(wx.EVT_KILL_FOCUS, lambda x: self.OnValueChange(2,x), self.input_N)
        self.input_dv.Bind(wx.EVT_KILL_FOCUS, lambda x: self.OnValueChange(3,x), self.input_dv)
    
    def OnValueChange(self, pos, event=None):
        """
        
            Actions triggered by value change in one of the text boxes.
            
            Parameters:
                pos    -    index of changed element (int)
                event  -    wx.Event
        
        """
        if event!=None: event.Skip()
        vmin = float(self.input_min.GetValue())
        vmax = float(self.input_max.GetValue())
        N = int(self.input_N.GetValue())
        dv = float(self.input_dv.GetValue())
        if pos==0:
            if vmax==vmin:
                vmin=vmax-1.0
        elif pos==1:
            if vmax==vmin:
                vmax=vmin+1.0
        elif pos==2:
            if N<1:
                N = 1
        elif pos==3 and dv!=0:
            N = int((vmax-vmin)/dv)+1
        dv = (vmax-vmin)/(N-1.0)
        self.input_min.SetValue(str(vmin))
        self.input_max.SetValue(str(vmax))
        self.input_N.SetValue(str(N))
        self.input_dv.SetValue(str(dv))

    def GetValue(self):
        """
        
            Return dialog values.
            
            Output:
                selected axis device index, start value (float), end value (float), number of steps (int), step size (float)
        
        """
        self.OnValueChange(0)
        return self.choice_axis.GetSelection(), float(self.input_min.GetValue()), float(self.input_max.GetValue()), int(self.input_N.GetValue()), float(self.input_dv.GetValue())
