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

    Device driver for Newport ESP300 motion controller
 
"""

from terapy.hardware.axes.base import AxisDevice
from wx import GetTextFromUser
from time import sleep

class ESP300(AxisDevice):
    """
    
        Device driver for Newport ESP300 motion controller
     
    """
    def __init__(self):
        AxisDevice.__init__(self)
        self.timeout = 2
        self.qtynames = "Position"
        self.units = "ps"
        self.instr = None
        self.psperunit = 6.6713
        self.config = ["psperunit"]
        self.last_position = 0
    
    def clear_errors(self):
        err = 1
        while(err != 0):
            err = int(self.instr.ask("TE?"))
    
    def initialize(self):
        # create device handle
        from visa import instrument
        self.instr = instrument(self.address)
        self.clear_errors()
        
        # check whether device is responding
        print "initiated", self.instr.ask(str(self.axis) + "VE"), "on port", self.address
        print "homing...", self.ID, ", axis", self.axis        
        self.write("MO")    # start the motor
        self.write("SH0")    # define HOME as zero
        self.write("OR2")    # go home            
    
    def reset(self):
        print "reinitialize.."
        self.initialize()
    
    def ask(self, cmd):
        cmdstr = str(self.axis) + cmd
        #while(result == "" or result[0:len(cmdstr)] != cmdstr):
        result = self.instr.ask(cmdstr)
        return result#[3:]
        
    def write(self, cmd):
        cmdstr = str(self.axis) + cmd
        self.instr.write(cmdstr)
        
    def get_motion_status(self):    
        sleep(0.1)
        try:
            status = int(self.ask("MD?"))
        except:
            status = 0
        if(status == 0):
            return 1    # moving
        return 0
        
    def stop(self):
        self.write("ST")
    
    def goTo(self, position, wait = False):
        if(self.get_motion_status() != 0):
            self.stop()
        print "goto:", position
        units = position / self.psperunit
        self.write("PA" + str(units))
        if(wait == True):
            while(self.get_motion_status() != 0 ):
                sleep(0.10)
        
    def jog(self, step):
        if(self.get_motion_status() != 0):
            self.stop()
        units = step / self.psperunit
        self.write("PR" + str(units))
        while(self.get_motion_status() != 0):
            sleep(0.1)
        return self.pos()
    
    def home(self):
        if(self.get_motion_status() != 0):
            self.stop()
        self.goTo(0)
    
    def pos(self):
        try:
            units = self.ask("TP")        
            units = float(units)
            self.last_position = units
        except:
            print "ERROR while reading position!"
            units = self.last_position
        return units * self.psperunit

    def configure(self):
        value = GetTextFromUser("Conversion factor for ps per unit (can be negative, 1mm in air (single pass) = 6.6713ps):", "SMC100 Config", default_value=str(self.psperunit))
        if value != "":
            try:
                value = float(value)
            except:
                value = 6.6713
            self.psperunit = value

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
                if (version.find("ESP300") != -1 ):
                    for ax in range(1,4): # motion controller - probe axes
                        #print "probe axis #%d" % (ax)
                        try:                        
                            print "probe ESP axis ", ax
                            ID = instr.ask(str(ax) + " ID?")
                            err = int(instr.ask("TE?"))
                            print " ..returns ", ID, " and error ", err
                            if(ID != "Unknown" and err == 0):
                                retval.append([handle,"Ax:"+str(ax)+" "+version,ax])
                        except:
                            print "exception"
        return retval
