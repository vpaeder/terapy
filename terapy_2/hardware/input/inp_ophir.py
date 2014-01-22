#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010-2013 Daniel Dietze
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

    Device driver for Ophir USB interface adapter

"""

from terapy.hardware.input.base import InputDevice
import wx
from time import sleep

# Ophir USBI Device        
class OphirDevice(InputDevice):
    """
    
        Device driver for Ophir USB interface adapter
    
    """
    def __init__(self):
        InputDevice.__init__(self)
        self.config = ['holdoff', 'mode', 'pulselength', 'wavelength', 'range', 'MM_mode', 'MM_samples', 'frequency']
        self.holdoff = 0.0
        self.mode = 0
        self.pulselength = 0
        self.wavelength = 0
        self.range = 0
        self.MM_mode = 0
        self.MM_samples = 1
        self.frequency = 1000
        self.units = ["V"]
        self.qtynames = [""]
        try:
            from ophir import OphirUSBI
            self.device = OphirUSBI()
            self.connected = False
        except:
            self.device = None
            self.connected = False
    
    def initialize(self):
        if self.device != None:
            try:
                self.device.connect(int(self.address))
                self.connected = True
                
                # apply settings
                self.device.set_measurement_mode(self.mode)
                self.device.set_wavelength(self.wavelength)
                self.device.set_pulse_length(self.pulselength)
                self.device.set_range(self.range)
                if(self.MM_mode == 0):
                    self.device.set_default_mode()
                elif(self.MM_mode == 1):
                    self.device.set_turbo_mode(self.frequency)
                else:
                    self.device.set_immediate_mode()
            except:
                self.connected = False

    def reset(self):
        if self.device != None and self.connected == True:
            self.device.reset()
            self.device.disconnect()
            self.device.connect()
    
    def get_error(self):
        return 0
        
    def read(self):        
        if self.device != None and self.connected == True:
            sleep(self.holdoff)
            data = self.device.read_data(self.MM_samples)        
            if data == []:
                return None
            if len(data[1]) > 1:                
                val = 0.0
                for i in range(len(data[1])):
                    val += data[1][i] / len(data[1])
                return [val]
            elif len(data[1]) == 1:
                return data[1]
            else:
                return None                        
        else:
            return None
    
    def configure(self):
        if self.device != None and self.connected == True:
            dlg = OphirConfig(self)
            if (dlg.ShowModal() == wx.ID_OK):
                # read settings from config dialog
                if dlg.txt_holdoff.GetValue() == "":
                    dlg.txt_holdoff.SetValue("0.0")
                if dlg.txt_MM_samples.GetValue() == "" or int(dlg.txt_MM_samples.GetValue()) < 1:
                    dlg.txt_MM_samples.SetValue("1")
                if dlg.txt_frequency.GetValue() == "" or int(dlg.txt_frequency.GetValue()) < 1:
                    dlg.txt_frequency.SetValue("1")
                
                self.holdoff = float(dlg.txt_holdoff.GetValue())
                self.MM_samples = int(dlg.txt_MM_samples.GetValue())
                self.frequency = float(dlg.txt_frequency.GetValue())
                self.mode = dlg.choice_mode.GetSelection()
                self.pulselength = dlg.choice_pulselength.GetSelection()
                self.wavelength = dlg.choice_wavelength.GetSelection()
                self.range = dlg.choice_range.GetSelection()
                self.MM_mode = dlg.choice_MM_mode.GetSelection()
                
                # apply new settings
                self.device.set_measurement_mode(self.mode)
                self.device.set_wavelength(self.wavelength)
                self.device.set_pulse_length(self.pulselength)
                self.device.set_range(self.range)
                if(self.MM_mode == 0):
                    self.device.set_default_mode()
                elif(self.MM_mode == 1):
                    self.device.set_turbo_mode(self.frequency)
                else:
                    self.device.set_immediate_mode()
                    
            dlg.Destroy()
            
    def detect(self):
        retval = []
        try:
            from ophir import OphirUSBI
            ophir = OphirUSBI()
            olist = ophir.scanUSBI()
            for i in range(len(olist)):
                # found device
                retval.append([str(i), "OphirUSBI", "Ophir" + olist[i]])
        except:
            pass
        return retval

class OphirConfig(wx.Dialog):
    def __init__(self, device):
        wx.Dialog.__init__(self, None, -1, 'Ophir Configuration')        
        mainSizer = wx.BoxSizer(wx.VERTICAL)        
        
        # data
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        label_1 = wx.StaticText(self, -1, "Waiting time before sample is recorded (s):")
        hbox1.Add(label_1, 0, wx.ALL | wx.EXPAND, 2)        
        self.txt_holdoff = wx.TextCtrl(self, -1, str(device.config['holdoff']), style = wx.TE_RIGHT)
        hbox1.Add(self.txt_holdoff, 1, wx.ALL | wx.EXPAND, 2)
        mainSizer.Add(hbox1, 0, wx.ALL | wx.EXPAND, 5)        
        
        # Ophir specific stuff
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        label_2 = wx.StaticText(self, -1, "Power Meter Mode:")
        hbox2.Add(label_2, 0, wx.ALL | wx.EXPAND, 2)        
        self.choice_mode = wx.Choice(self, -1, choices=device.device.MM_Modes)
        self.choice_mode.SetSelection(device.config['mode'])
        hbox2.Add(self.choice_mode, 1, wx.ALL | wx.EXPAND, 2)
        mainSizer.Add(hbox2, 0, wx.ALL | wx.EXPAND, 5)
        
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        label_3 = wx.StaticText(self, -1, "Pulse Length:")
        hbox3.Add(label_3, 0, wx.ALL | wx.EXPAND, 2)        
        self.choice_pulselength = wx.Choice(self, -1, choices=device.device.MM_PulseLengths)
        self.choice_pulselength.SetSelection(device.config['pulselength'])
        hbox3.Add(self.choice_pulselength, 1, wx.ALL | wx.EXPAND, 2)
        mainSizer.Add(hbox3, 0, wx.ALL | wx.EXPAND, 5)
        
        hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        label_4 = wx.StaticText(self, -1, "Wavelength:")
        hbox4.Add(label_4, 0, wx.ALL | wx.EXPAND, 2)        
        self.choice_wavelength = wx.Choice(self, -1, choices=device.device.MM_Wavelengths)
        self.choice_wavelength.SetSelection(device.config['wavelength'])
        hbox4.Add(self.choice_wavelength, 1, wx.ALL | wx.EXPAND, 2)
        mainSizer.Add(hbox4, 0, wx.ALL | wx.EXPAND, 5)
        
        hbox5 = wx.BoxSizer(wx.HORIZONTAL)
        label_5 = wx.StaticText(self, -1, "Range:")
        hbox5.Add(label_5, 0, wx.ALL | wx.EXPAND, 2)        
        self.choice_range = wx.Choice(self, -1, choices=device.device.MM_Ranges)
        self.choice_range.SetSelection(device.config['range'])
        hbox5.Add(self.choice_range, 1, wx.ALL | wx.EXPAND, 2)
        mainSizer.Add(hbox5, 0, wx.ALL | wx.EXPAND, 5)
        
        hbox6 = wx.BoxSizer(wx.HORIZONTAL)
        label_6 = wx.StaticText(self, -1, "Measurement Mode:")
        hbox6.Add(label_6, 0, wx.ALL | wx.EXPAND, 2)        
        self.choice_MM_mode = wx.Choice(self, -1, choices=["Default", "Turbo", "Immediate"])
        self.choice_MM_mode.SetSelection(device.config['MM_mode'])
        hbox6.Add(self.choice_MM_mode, 1, wx.ALL | wx.EXPAND, 2)
        mainSizer.Add(hbox6, 0, wx.ALL | wx.EXPAND, 5)
        
        hbox7b = wx.BoxSizer(wx.HORIZONTAL)
        label_7b = wx.StaticText(self, -1, "Expected Frequency for Turbo Mode (Hz):")
        hbox7b.Add(label_7b, 0, wx.ALL | wx.EXPAND, 2)        
        self.txt_frequency = wx.TextCtrl(self, -1, str(device.config['frequency']), style = wx.TE_RIGHT)
        hbox7b.Add(self.txt_frequency, 1, wx.ALL | wx.EXPAND, 2)
        mainSizer.Add(hbox7b, 0, wx.ALL | wx.EXPAND, 5)
        
        hbox7 = wx.BoxSizer(wx.HORIZONTAL)
        label_7 = wx.StaticText(self, -1, "Number of samples:")
        hbox7.Add(label_7, 0, wx.ALL | wx.EXPAND, 2)        
        self.txt_MM_samples = wx.TextCtrl(self, -1, str(device.config['MM_samples']), style = wx.TE_RIGHT)
        hbox7.Add(self.txt_MM_samples, 1, wx.ALL | wx.EXPAND, 2)
        mainSizer.Add(hbox7, 0, wx.ALL | wx.EXPAND, 5)
        
        # buttons
        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)                
        cancel_button = wx.Button(self, wx.ID_CANCEL, "Cancel")        
        buttonSizer.Add(cancel_button, 0, wx.ALL | wx.ALIGN_CENTER, 2)
        ok_button = wx.Button(self, wx.ID_OK, "Apply")
        buttonSizer.Add(ok_button, 0, wx.ALL | wx.ALIGN_CENTER, 2)                
        mainSizer.Add(buttonSizer, 0, wx.ALL | wx.ALIGN_CENTER, 2)
        
        # layout
        self.SetSizer(mainSizer)
        self.Layout()
        self.Fit()    
