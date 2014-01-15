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

    Device driver for Agilent E3647A power supply
 
"""

from terapy.hardware.axes.base import AxisDevice
from time import sleep

class E3647A(AxisDevice):
    """
    
        Device driver for Agilent E3647A power supply
     
    """
    # As an "axis" device, can be used to test the behaviour of antennas vs bias automatically
    def __init__(self):
        AxisDevice.__init__(self)
        self.timeout = 1.0
        self.qtynames = "Voltage"
        self.units = "V"
        self.instr = None
        self.config = []
    
    def initialize(self):
        # create device handle
        from visa import instrument
        self.instr = instrument(self.address)
        # set both outputs to 0V and enable output tracking
        self.instr.write("INST:NSEL 1")
        self.instr.write("VOLT:TRIG 0.0")
        self.instr.write("INST:NSEL 2")
        self.instr.write("VOLT:TRIG 0.0")
        self.instr.write("TRIG:SOUR IMM")
        self.instr.write("INIT")
        self.instr.write("OUTP:TRAC ON")
        # set high voltage mode
        self.instr.write("INST:NSEL 1")
        self.instr.write("VOLT:RANG P60V")
        # enable outputs
        self.instr.write("OUTP ON")
        
    def write(self, cmd):
        self.instr.write(cmd)
    
    def configure(self):
        pass
    
    def reset(self):
        print "reinitialize.."
        self.initialize()
    
    def ask(self, cmd):
        result = self.instr.ask(cmd)
        return result
        
    def jog(self, step):
        step = float(step)
        if step<0:
            self.write("VOLT:STEP " + str(-step))
            self.write("VOLT DOWN")
        else:
            self.write("VOLT:STEP " + str(step))
            self.write("VOLT UP")
        return self.pos()
    
    def get_motion_status(self):
        status = self.ask("*OPC?")
        status = 1-int(status)
        return status
    
    def pos(self):
        pos = self.ask("VOLT?")
        pos = float(pos)
        return pos
        
    def goTo(self, position, wait = False):
        print "set voltage to:", position
        self.write("VOLT " + str(float(position)))
        sleep(1.0)

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
                if (version.find("E3647A") != -1 ):
                    retval.append([handle,version,0])
        return retval

