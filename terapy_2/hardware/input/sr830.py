#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010-2013 Daniel Dietze, 2013-2014  Vincent Paeder
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

    Device driver for Stanford Research Systems SR830 Lock-In Amplifier
 
"""

from terapy.hardware.input.base import InputDevice
import wx
from time import sleep

# Stanford SR830 Lock In
class SR830(InputDevice):
    """
    
        Device driver for Stanford Research Systems SR830 Lock-In Amplifier
     
    """
    def __init__(self):
        InputDevice.__init__(self)
        self.timeout = 2
        self.units = ["V", "V", "V", "deg"]
        self.qtynames = ["X","Y","R","phi"]
        self.instr = None
        self.holdoff = 0.0
        self.channel = 0
        self.automatic = False
        self.config = ["holdoff","channel","automatic"]
    
    def initialize(self):
        from visa import instrument
        # create device handle
        self.instr = instrument(self.address)
        # reset
        self.instr.write("REST")
        # print notice
        print "initiated", self.instr.ask("*IDN?"), "on port", self.address
    
    def reset(self):
        # reset
        self.instr.write("REST")
        
    def get_error(self):
        return self.instr.ask("ERRS?")
    
    def get_time_const(self):
        """
        
            Get time constant.
            
            Output:
                Time constant (float)
        
        """
        vlist = [1e-5,3e-5,1e-4,3e-4,1e-3,3e-3,1e-2,3e-2,1e-1,3e-1,1,3,10,30,100,300,1e3,3e3,1e4,3e4]
        vl = self.instr.ask("OFLT?")
        return vlist[int(vl)]
    
    def set_time_const(self,tc):
        """
        
            Set time constant.
            
            Parameters:
                tc    -    Time constant (float)
        
        """
        vlist = [1e-5,3e-5,1e-4,3e-4,1e-3,3e-3,1e-2,3e-2,1e-1,3e-1,1,3,10,30,100,300,1e3,3e3,1e4,3e4]
        try:
            vlist.index(tc)
        except:
            return False
        id = vlist.index(tc)
        self.instr.write("OFLT "+str(id))
        vl = self.instr.ask("OFLT?")
        if vl==id:
            return True
        else:
            return False
    
    def update_holdoff(self):
        """
        
            Update hold off time.
        
        """
        tc = self.get_time_const()
        self.holdoff = 5.0 * tc
    
    def read(self):        
        sleep(self.holdoff)
        # query X,Y,R and Phi
        valuelist = self.instr.ask('SNAP?1,2,3,4')
        if valuelist == "":
            return 0.0
        values = map(float, valuelist.split(','))
        return values
    
    def configure(self):
        dlg = SR830config(self)        
        if (dlg.ShowModal() == wx.ID_OK):
            if(dlg.txt_holdoff.GetValue() != ""):
                value = float(dlg.txt_holdoff.GetValue())
            else:
                value = 0.0
            self.holdoff = value
            self.channel = dlg.choice_channel.GetSelection()
            self.automatic = dlg.check_automatic.GetValue()
        dlg.Destroy()
        self.update_holdoff()

    def detect(self):
        try:
            from visa import get_instruments_list, instrument
        except:
            return []
         
        devlist = get_instruments_list()
        retval = []
        for handle in devlist:
            if (handle.find("GPIB") != -1):
                instr  = instrument(handle)
                version = instr.ask("*IDN?")
                if (version.find("SR830") != -1 ):
                    retval.append([handle,version])
        return retval
    
class SR830config(wx.Dialog):
    """
    
        SR830 configuration dialog
    
    """
    def __init__(self, device):
        wx.Dialog.__init__(self, None, -1, 'SR830 Configuration')        
        mainSizer = wx.BoxSizer(wx.VERTICAL)        
        
        # data
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        label_1 = wx.StaticText(self, -1, "Waiting time before sample is recorded (s):")
        hbox1.Add(label_1, 0, wx.ALL | wx.EXPAND, 2)        
        self.txt_holdoff = wx.TextCtrl(self, -1, str(device.config['holdoff']), style = wx.TE_RIGHT)
        hbox1.Add(self.txt_holdoff, 1, wx.ALL | wx.EXPAND, 2)
        mainSizer.Add(hbox1, 0, wx.ALL | wx.EXPAND, 5)
        
        hbox1b = wx.BoxSizer(wx.HORIZONTAL)
        self.check_automatic = wx.CheckBox(self, -1, "Set waiting time automatically!")
        self.check_automatic.SetValue(bool(device.config['automatic']))
        hbox1b.Add(self.check_automatic, 1, wx.ALL | wx.EXPAND, 2)
        mainSizer.Add(hbox1b, 0, wx.ALL | wx.EXPAND, 5)
        
        self.check_box()
        
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        label_2 = wx.StaticText(self, -1, "Input Channel:")
        hbox2.Add(label_2, 0, wx.ALL | wx.EXPAND, 2)        
        self.choice_channel = wx.Choice(self, -1, choices=["X", "Y", "R", "PHI"])
        self.choice_channel.SetSelection(device.config['channel'])
        hbox2.Add(self.choice_channel, 1, wx.ALL | wx.EXPAND, 2)
        mainSizer.Add(hbox2, 0, wx.ALL | wx.EXPAND, 5)        
        
        # buttons
        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)                
        cancel_button = wx.Button(self, wx.ID_CANCEL, "Cancel")        
        buttonSizer.Add(cancel_button, 0, wx.ALL | wx.ALIGN_CENTER, 2)
        ok_button = wx.Button(self, wx.ID_OK, "Apply")
        buttonSizer.Add(ok_button, 0, wx.ALL | wx.ALIGN_CENTER, 2)
        mainSizer.Add(buttonSizer, 0, wx.ALL | wx.ALIGN_CENTER, 2)
        
        # check event
        self.Bind(wx.EVT_CHECKBOX, self.check_box, self.check_automatic)
        
        # layout
        self.SetSizer(mainSizer)
        self.Layout()
        self.Fit()        
    
    def check_box(self, event = None):
        self.txt_holdoff.Enable(not self.check_automatic.GetValue())

