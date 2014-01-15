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

    Generic input device driver

"""

import random
from time import time
import wx
from terapy.hardware.device import Device
from terapy.core import icon_path
from terapy.core.validator import NumberValidator

# generic input device
class InputDevice(Device):
    """
    
        Generic input device driver
    
    """
    def __init__(self):
        self.address = None
        self.ID = None
        self.name = ""
        self.units = ["V"]
        self.qtynames = ["X"]
        self.amplitude = 1.0
        self.config = ['amplitude']
    
    def assign(self, address, ID, name):
        """
        
            Configure device driver prior to initialization.
            
            Parameters:
                address    -    physical address as required by communication interface driver
                ID         -    device short name (str)
                name       -    device long name (str)
        
        """
        self.address = address
        self.ID = ID
        self.name = name
    
    def initialize(self):
        """
        
            Initialize device.
        
        """
        random.seed(time())

    def read(self):        
        """
        
            Return values read by device.
            
            Output:
                Device values (list of floats)
        
        """
        return [(random.random() - 0.5) * self.amplitude]
    
    def get_units(self, idx=0):
        """
        
            Return infos and units on meaningful quantity
            
            Output:
                (description (str), units (quantities))
        
        """
        return (self.qtynames[idx], self.units[idx])

    def state(self):
        """
        
            Return extended snapshot of device.
            
            Output:
                list of tuples, each qty as (name, value, units)
        
        """
        return zip(self.qtynames, self.read(), self.units)
    
    def configure(self):
        """
        
            Call device configuration dialog.
        
        """
        value = wx.GetTextFromUser("Peak-Peak-Amplitude:", "Random Numbers Config", default_value=str(self.amplitude))
        if value != "":
            try:
                value = float(value)
            except:
                value = 1.0
            self.amplitude = value
    
    def widget(self, parent=None):
        """
        
            Return widget for graphical device control.
            
            Parameters:
                parent    -    parent window (wx.Window)
                
            Output:
                widget (wx.Frame)
        
        """
        if not(self.ID=="RANDOM"):
            try:
                return [InputWidget(parent,units=self.units, qtynames=self.qtynames, title=self.ID + ": " +self.name, input = self)]
            except:
                return None

class InputWidget(wx.ScrolledWindow):
    """
    
        Input device widget class
    
    """
    def __init__(self,parent=None, units=["V"], qtynames=["X"], title="", input = None, min = None, max = None):
        """
        
            Initialization.
            
            Parameters:
                parent    -    parent window (wx.Window)
                units     -    units of read quantities (list of str)
                qtynames  -    name of read quantities (list of str)
                title     -    widget title (str)
                input     -    input to be read (not used for now)
                min       -    minimum value (float)
                max       -    maximum value (float)
        
        """
        wx.ScrolledWindow.__init__(self,parent,style=wx.HSCROLL|wx.VSCROLL|wx.TAB_TRAVERSAL)
        self.units = units
        self.qtynames = qtynames
        self.title = title
        self.input = input
        self.min = min
        self.max = max
        self.scales = ["f","p","n","u","m","","k","M","G","T"]
        self.scalesval = [1e-15,1e-12,1e-9,1e-6,1e-3,1.0,1.0e3,1.0e6,1.0e9,1.0e12]
        self.timer = wx.Timer()
        
        self.SetScrollbars(1,1,1,1)
        self.label_value = []
        for x in units:
            self.label_value.append(wx.StaticText(self,-1,""))
            self.label_value[-1].SetMinSize((200,-1))
        f = self.label_value[0].GetFont()
        f.SetPointSize(18)
        f.SetFamily(wx.FONTFAMILY_TELETYPE)
        f.SetWeight(wx.FONTWEIGHT_BOLD)
        for x in self.label_value:
            x.SetFont(f)
        self.button_reset = wx.BitmapButton(self, -1, wx.Image(icon_path + "reset.png").ConvertToBitmap())
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox2 = wx.GridSizer(rows=1,cols=len(units),hgap=5)
        
        hbox.Add(self.button_reset,0,wx.ALIGN_CENTER_VERTICAL,2)
        hbox.Add(wx.StaticLine(self,-1,style=wx.LI_VERTICAL),0,wx.ALL|wx.EXPAND,2)
        
        for x in self.label_value:
            hbox2.Add(x,0,wx.ALIGN_CENTER_VERTICAL|wx.ALL,2)
        
        sbox = wx.StaticBox(self,-1,"Current value" + ["","s"][len(units)>1])
        vbox2 = wx.StaticBoxSizer(sbox,wx.HORIZONTAL)
        vbox2.Add(hbox2,0,wx.ALIGN_CENTER_VERTICAL|wx.ALL,2)
        hbox.Add(vbox2,0,wx.EXPAND|wx.ALL,2)
        
        self.SetSizerAndFit(hbox)
        
        self.button_reset.Bind(wx.EVT_BUTTON, self.OnReset, self.button_reset)
        self.timer.Bind(wx.EVT_TIMER, self.RefreshDisplay, self.timer)
        
        self.timer.Start(250)
    
    def RefreshDisplay(self, event = None):
        """
        
            Refresh display.
            
            Parameters:
                event    -    wx.Event
        
        """
        try:
            val = self.input.read()
        except:
            val = [0]
        
        if not(hasattr(val,'__len__')):
            val = [val]
        
        for n in range(len(val)):
            sidx = [i for i in map(lambda x:int(val[n]/x),self.scalesval)].index(0)-1 # index of unit scale
            if sidx==-1: sidx=0
            curval = self.qtynames[n] + [": ",""][self.qtynames[n]==""] + ("%3.2f" % (val[n]/self.scalesval[sidx])) + " " + self.scales[sidx] + self.units[n]
            self.label_value[n].SetLabel(curval)
    
    def OnReset(self, event = None):
        """
        
            Actions triggered when Reset button is pressed.
            
            Parameters:
                event    -    wx.Event
        
        """
        self.input.reset()
    
class AntennaWidget(wx.ScrolledWindow):
    """
    
        Antenna device widget class
    
    """
    def __init__(self,parent=None, units="V", title="", amp = "0", device = None, min = None, max = None):
        """
        
            Initialization.
            
            Parameters:
                parent    -    parent window (wx.Window)
                units     -    units of quantity to handle (str)
                title     -    widget title (str)
                amp       -    default value (str)
                device    -    device to be handled (not used for now)
                min       -    minimum value (float)
                max       -    maximum value (float)
        
        """
        wx.ScrolledWindow.__init__(self,parent,style=wx.HSCROLL|wx.VSCROLL)
        self.units = units
        self.title = title
        self.device = device
        self.min = min
        self.max = max
        self.timer = wx.Timer()
        
        self.SetScrollbars(1,1,1,1)
        self.label_amplitude = wx.StaticText(self,-1, amp + " " + units)
        f = self.label_amplitude.GetFont()
        f.SetPointSize(18)
        f.SetWeight(wx.FONTWEIGHT_BOLD)
        self.label_amplitude.SetFont(f)
        self.input_amplitude = wx.SpinCtrl(self,-1,amp, validator=NumberValidator(), style=wx.TE_PROCESS_ENTER|wx.SP_ARROW_KEYS)
        self.button_go = wx.BitmapButton(self, -1, wx.Image(icon_path + "go.png").ConvertToBitmap())
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        vbox2 = wx.BoxSizer(wx.VERTICAL)
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        
        hbox2.Add(self.input_amplitude,0,wx.CENTER|wx.VERTICAL,2)
        hbox2.Add(self.button_go,0,wx.CENTER|wx.VERTICAL,2)
        vbox2.Add(wx.StaticText(self,-1,"Set amplitude ("+units+")"), 0, wx.EXPAND|wx.ALL, 5)
        vbox2.Add(hbox2,0,wx.EXPAND|wx.ALL,2)
        
        hbox.Add(vbox2,0,wx.CENTER|wx.ALL,2)
        hbox.Add(wx.StaticLine(self,-1,style=wx.LI_VERTICAL),0,wx.ALL|wx.EXPAND,2)
        hbox.Add(self.label_amplitude,0,wx.CENTER|wx.ALL,2)
        
        self.SetSizer(hbox)
        
        self.button_go.Bind(wx.EVT_BUTTON, self.OnGo, self.button_go)
        self.input_amplitude.Bind(wx.EVT_TEXT_ENTER, self.OnGo, self.input_amplitude)
        self.input_amplitude.Bind(wx.EVT_KILL_FOCUS, self.OnSet, self.input_amplitude)
        self.timer.Bind(wx.EVT_TIMER, self.RefreshDisplay, self.timer)
        
        self.timer.Start(250)
        
    def RefreshDisplay(self, event = None):
        """
        
            Refresh display.
            
            Parameters:
                event    -    wx.Event
        
        """
        try:
            amp = self.device.get_amplitude()
        except:
            amp = 0
        self.label_amplitude.SetLabel(str(amp) + " " + self.units)
    
    def OnGo(self, event = None):
        """
        
            Actions triggered when Go button is pressed.
            
            Parameters:
                event    -    wx.Event
        
        """
        self.OnSet(event)
        try:
            self.device.set_amplitude(float(self.input_amplitude.GetValue()))
        except:
            pass
        event.Skip()
    
    def OnSet(self, event = None):
        """
        
            Actions triggered when widget value is changed.
            
            Parameters:
                event    -    wx.Event
        
        """
        if float(self.input_amplitude.GetValue())<self.min and self.min!=None:
            self.input_amplitude.SetValue(str(self.min))
        if float(self.input_amplitude.GetValue())>self.max and self.max!=None:
            self.input_amplitude.SetValue(str(self.max))
        event.Skip()
    