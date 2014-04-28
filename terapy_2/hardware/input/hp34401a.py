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

    Driver for HP Agilent Multimeter 34401A

"""

from terapy.hardware.input.base import InputDevice
import wx
from time import sleep

# HP Multimeter
class HP34401A(InputDevice):
    """
    
        Driver for HP Agilent Multimeter 34401A
    
    """
    def __init__(self):
        InputDevice.__init__(self)
        self.timeout = 2
        self.instr = None        
        self.units = ["V"]
        self.qtynames = [""]
        self.holdoff = 0.0
        self.config = ['holdoff']
        
    def initialize(self):
        # create device handle
        from visa import instrument
        self.instr = instrument(self.address)
        # reset
        self.instr.write("*RST")
        # print notice
        print "initiated", self.instr.ask("*IDN?"), "on port", self.address
    
    def reset(self):
        # reset
        self.instr.write("*RST")
    
    def get_error(self):
        return self.instr.ask("SYST:ERR?")
        
    def read(self):
        sleep(self.holdoff)
        value = self.instr.ask('READ?')
        if value != "":
            value = float(value)
        else:    
            value = 0.0
        return [value]
    
    def configure(self):
        value = wx.GetTextFromUser("Waiting time before sample is recorded (s):", "HP34401A Config", default_value=str(self.holdoff))
        if value != "":
            try:
                value = float(value)
            except:
                value = 0.0
            self.holdoff = value

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
                if (version.find("34401A") != -1 ):
                    retval.append([handle,version])
        return retval

