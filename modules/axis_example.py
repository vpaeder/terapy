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
    Axis device driver example 
"""

from terapy.hardware.axes.base import AxisDevice

class AxisExample(AxisDevice):
    """
        Axis device driver example 
    """
    def __init__(self):
        AxisDevice.__init__(self)
        # Insert here what the driver should do when loaded
        # (e.g. check that the right modules/interface cards/... are present).
        # DON'T initialize the device here (see initialize() function for that).
        
        self.qtynames = "Position" # name of returned quantities
        self.units = "ps" # units of axis readings
        
        # variables stated in self.config will be loaded/saved
        # from/to the configuration file (devices.ini)
        self.config = ["variable1", "variable2"]
        self.variable1 = 0.0
        self.variable2 = "blah"
    
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
        
    def initialize(self):
        """
            Initialize device.
        """
        pass
        
    def configure(self):
        """
            Run configuration routine for device.
        """
        pass

    def detect(self):
        """
            Detect available devices handled by device driver.
            Output:
                list of available devices, each entry as (address, short name, long name, axis id)
        """
        return []
    
    def reset(self):
        """
            Reset device.
        """
        pass
    
    def ask(self, cmd):
        """
            Send given command to instrument and return result.
            Parameters:
                cmd    -    command (str)
            Output:
                instrument reply (float)
        """
        return 0
        
    def write(self, cmd):
        """
            Send given command to instrument.
            Parameters:
                cmd    -    command (str)
        """
        pass
    
    def jog(self, step):
        """
            Jog device relative to current position by given amount.
            Parameters:
                step    -    movement size (float)
        """
        pass
    
    def get_motion_status(self):
        """
            Return current state of device.
            Output:
                device response to status polling
        """
        return 0 
    
    def pos(self):
        """
            Return current position of device.
            Output:
                Device position (float)
        """
        return 0
    
    def stop(self):
        """
            Stop device movement.
        """
        pass
    
    def prepareScan(self):
        """
            Prepare device for scanning.
        """
        pass
    
    def goTo(self, position, wait = False):
        """
            Set device position to given position.
            Parameters:
                position    -    position (float)
                wait        -    if True, wait that device reaches position before return
        """
        pass

