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

    Generic axis device driver
 
"""

from time import time, sleep
import wx
from terapy.hardware.device import Device
from terapy.core import icon_path
from terapy.core.validator import NumberValidator

# generic axis device, motion controller - GPIB and COM
class AxisDevice(Device):
    """
    
        Generic axis device driver
     
    """
    def __init__(self):
        self.timerStart = 0 
        self.intervalTimerStart = 0
        self.qtynames = "Time"
        self.units = "s"
        self.interval = 0.01
        self.config = ["interval"]
    
    def assign(self, address, ID, name, axis):
        """
        
            Configure device driver prior to initialization.
            
            Parameters:
                address    -    physical address as required by communication interface driver
                ID         -    device short name (str)
                name       -    device long name (str)
                axis       -    axis id (int)
        
        """
        self.address = address
        self.ID = ID
        self.name = name
        self.axis = axis
        
    def get_motion_status(self):
        """
        
            Return current state of device.
            
            Output:
                device response to status polling
        
        """
        if(time() - self.intervalTimerStart < self.interval):
            return 1
        else:
            self.intervalTimerStart = time()
            return 0
    
    def get_units(self, idx=0):
        """
        
            Return infos and units on meaningful quantity
            
            Output:
                (description (str), units(quantities))
        
        """
        return (self.qtynames, self.units)
    
    def prepareScan(self):
        """
        
            Prepare device for scanning.
        
        """
        self.timerStart = time()
        self.intervalTimerStart = time()
        
    def goTo(self, position, wait=False):
        """
        
            Set device position to given position.
            
            Parameters:
                position    -    position (float)
                wait        -    if True, wait that device reaches position before return
        
        """
        self.intervalTimerStart = time()
        if(wait == True):
            while(time() - self.intervalTimerStart < self.interval):
                sleep(0.001)
                
    def home(self):
        """
        
            Home device.
        
        """
        pass

    def stop(self):
        """
        
            Stop device movement.
        
        """
        pass
    
    def jog(self, step):
        """
        
            Jog device relative to current position by given amount.
            
            Parameters:
                step    -    movement size (float)
        
        """
        return 0.0
        
    def pos(self):
        """
        
            Return current position of device.
            
            Output:
                Device position (float)
        
        """
        return time() - self.timerStart
    
    def state(self):
        """
        
            Return extended snapshot of device.
            
            Output:
                list of tuples, each qty as (name, value, units)
        
        """
        return [(self.qtynames, self.pos(), self.units)]
    
    def configure(self):
        """
        
            Call device configuration dialog.
        
        """
        value = wx.GetTextFromUser("Sampling Interval (s):", "Sampling Interval Config", default_value=str(self.interval))
        if value != "":
            try:
                value = float(value)
            except:
                value = 1.0
            self.interval = value
    
    def widget(self, parent=None):
        """
        
            Return widget for graphical device control.
            
            Parameters:
                parent    -    parent window (wx.Window)
            
            Output:
                widget (wx.Frame)
        
        """
        if not(self.ID=="TIME"):
            try:
                return [AxisWidget(parent,qtyname=self.qtynames, units=self.units, title=self.ID + ": " +self.name, pos = str(self.pos()), axis = self)]
            except:
                return None

class AxisWidget(wx.ScrolledWindow):
    """
    
        Axis device widget class
    
    """
    def __init__(self,parent=None, qtyname="Position", units="ps", title="", pos = "0", axis = None, min = None, max = None):
        """
        
            Initialization.
            
            Parameters:
                parent    -    parent window (wx.Window)
                qtyname   -    name of quantity to handle (str)
                units     -    units of quantity to handle (quantities units)
                title     -    widget title (str)
                pos       -    default position (str)
                axis      -    axis to be controlled (not used for now)
                min       -    minimum value (float)
                max       -    maximum value (float)
        
        """
        wx.ScrolledWindow.__init__(self,parent,style=wx.HSCROLL|wx.VSCROLL|wx.TAB_TRAVERSAL)
        self.units = units
        self.title = title
        self.axis = axis
        self.min = min
        self.max = max
        self.qtyname = qtyname[0].lower() + qtyname[1:]
        self.timer = wx.Timer()
        
        self.SetScrollbars(1,1,1,1)
        self.label_position = wx.StaticText(self,-1,pos + " " + units)
        f = self.label_position.GetFont()
        f.SetPointSize(18)
        f.SetWeight(wx.FONTWEIGHT_BOLD)
        self.label_position.SetFont(f)
        self.input_position = wx.TextCtrl(self,-1,pos, validator=NumberValidator(), style=wx.TE_PROCESS_ENTER)
        self.button_go = wx.BitmapButton(self, -1, wx.Image(icon_path + "go.png").ConvertToBitmap())
        self.button_stop = wx.BitmapButton(self, -1, wx.Image(icon_path + "stop.png").ConvertToBitmap())
        self.button_home = wx.BitmapButton(self, -1, wx.Image(icon_path + "home.png").ConvertToBitmap())
        self.button_reset = wx.BitmapButton(self, -1, wx.Image(icon_path + "reset.png").ConvertToBitmap())
        self.input_jog = wx.TextCtrl(self,-1,"0", validator=NumberValidator(), style=wx.TE_PROCESS_ENTER)
        self.button_left = wx.BitmapButton(self, -1, wx.Image(icon_path + "left.png").ConvertToBitmap())
        self.button_right = wx.BitmapButton(self, -1, wx.Image(icon_path + "right.png").ConvertToBitmap())
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        vbox2 = wx.BoxSizer(wx.VERTICAL)
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        vbox3 = wx.BoxSizer(wx.VERTICAL)
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        
        hbox2.Add(self.input_position,0,wx.CENTER|wx.VERTICAL,2)
        hbox2.Add(self.button_go,0,wx.CENTER|wx.VERTICAL,2)
        hbox2.Add(self.button_stop,0,wx.CENTER|wx.VERTICAL,2)
        hbox2.Add(self.button_home,0,wx.CENTER|wx.VERTICAL,2)
        hbox2.Add(self.button_reset,0,wx.CENTER|wx.VERTICAL,2)
        vbox2.Add(wx.StaticText(self,-1,"Set "+self.qtyname+" ("+units+")"), 0, wx.EXPAND|wx.ALL, 5)
        vbox2.Add(hbox2,0,wx.EXPAND|wx.ALL,2)
        
        hbox3.Add(self.input_jog,0,wx.CENTER|wx.VERTICAL,2)
        hbox3.Add(self.button_left,0,wx.CENTER|wx.VERTICAL,2)
        hbox3.Add(self.button_right,0,wx.CENTER|wx.VERTICAL,2)
        vbox3.Add(wx.StaticText(self,-1,"Jog ("+units+")"), 0, wx.EXPAND|wx.ALL, 5)
        vbox3.Add(hbox3,0,wx.EXPAND|wx.ALL,2)
        
        hbox.Add(vbox2,0,wx.CENTER|wx.ALL,2)
        hbox.Add(wx.StaticLine(self,-1,style=wx.LI_VERTICAL),0,wx.ALL|wx.EXPAND,2)
        hbox.Add(vbox3,0,wx.CENTER|wx.ALL,2)
        hbox.Add(wx.StaticLine(self,-1,style=wx.LI_VERTICAL),0,wx.ALL|wx.EXPAND,2)
        hbox.Add(self.label_position,0,wx.CENTER|wx.ALL,2)
        
        self.SetSizer(hbox)
        
        self.button_go.Bind(wx.EVT_BUTTON, self.OnGo, self.button_go)
        self.button_stop.Bind(wx.EVT_BUTTON, self.OnStop, self.button_stop)
        self.button_home.Bind(wx.EVT_BUTTON, self.OnHome, self.button_home)
        self.button_reset.Bind(wx.EVT_BUTTON, self.OnReset, self.button_reset)
        self.button_left.Bind(wx.EVT_BUTTON, self.OnLeft, self.button_left)
        self.button_right.Bind(wx.EVT_BUTTON, self.OnRight, self.button_right)
        self.input_position.Bind(wx.EVT_TEXT_ENTER, self.OnGo, self.input_position)
        self.input_position.Bind(wx.EVT_KILL_FOCUS, self.OnSet, self.input_position)
        self.timer.Bind(wx.EVT_TIMER, self.RefreshDisplay, self.timer)
        
        self.timer.Start(250)
        
    def RefreshDisplay(self, event = None):
        """
        
            Refresh display.
            
            Parameters:
                event    -    wx.Event
        
        """
        try:
            pos = self.axis.pos()
        except:
            pos = 0
        self.label_position.SetLabel(("%3.2f" % pos) + " " + self.units)
        
    def SetValue(self, val):
        """
        
            Set device and widget values.
            
            Parameters:
                val    -    value (float)
        
        """
        self.input_position.SetValue(str(val))
        self.OnGo()
    
    def OnGo(self, event = None):
        """
        
            Actions triggered when Go button is pressed.
            
            Parameters:
                event    -    wx.Event
        
        """
        self.OnSet(event)
        try:
            self.axis.goTo(float(self.input_position.Value))
        except:
            pass
        if event!=None:
            event.Skip()
    
    def OnHome(self, event = None):
        """
        
            Actions triggered when Home button is pressed.
            
            Parameters:
                event    -    wx.Event
        
        """
        self.axis.home()
        val = self.axis.pos()
        self.input_position.SetValue(str(val))

    def OnReset(self, event = None):
        """
        
            Actions triggered when Reset button is pressed.
            
            Parameters:
                event    -    wx.Event
        
        """
        self.axis.reset()
        val = self.axis.pos()
        self.input_position.SetValue(str(val))
    
    def OnSet(self, event = None):
        """
        
            Actions triggered when widget value is changed.
            
            Parameters:
                event    -    wx.Event
        
        """
        if float(self.input_position.GetValue())<self.min and self.min!=None:
            self.input_position.SetValue(str(self.min))
        if float(self.input_position.GetValue())>self.max and self.max!=None:
            self.input_position.SetValue(str(self.max))
        if event!=None:
            event.Skip()
        
    def OnStop(self, event = None):
        """
        
            Actions triggered when Stop button is pressed.
            
            Parameters:
                event    -    wx.Event
        
        """
        self.axis.stop()
    
    def OnLeft(self, event = None):
        """
        
            Actions triggered when Jog left button is pressed.
            
            Parameters:
                event    -    wx.Event
        
        """
        val = float(self.input_position.Value) - float(self.input_jog.Value)
        self.input_position.SetValue(str(val))
        self.OnGo(event)

    def OnRight(self, event = None):
        """
        
            Actions triggered when Jog right button is pressed.
            
            Parameters:
                event    -    wx.Event
        
        """
        val = float(self.input_position.Value) + float(self.input_jog.Value)
        self.input_position.SetValue(str(val))
        self.OnGo(event)
