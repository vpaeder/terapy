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
    Input device driver example
"""

from terapy.hardware.input.base import InputDevice

class InputExample(InputDevice):
    """
        Input device driver example
    """
    def __init__(self):
        """
            Initialization.
        """
        InputDevice.__init__(self)
        # Insert here what the driver should do when loaded
        # (e.g. check that the right modules/interface cards/... are present).
        # DON'T initialize the device here (see initialize() function for that).
        
        # variables stated in self.config will be loaded/saved
        # from/to the configuration file (devices.ini)
        self.config = ["variable1", "variable2"]
        self.variable1 = 0.0
        self.variable2 = "blah"
    
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
        pass        
    
    def reset(self):
        """
            Reset device.
        """
        pass
    
    def read(self):
        """
            Return values read by device.
            Output:
                Device values (list of floats)
        """
        # Return what is read as a list of floats.
        # This list can be used by a scan event in the way you like.
        # For example:
        #    -    device reads several quantities at once => pick the one of interest
        #    -    device reads the same source multiple times => compute average/variance/...
        return [0]
    
    def detect(self):
        """
            Detect available devices handled by device driver.
            Output:
                list of available devices, each entry as (address, short name, long name)
        """
        return []
    
    def configure(self):
        """
            Call device configuration dialog.
        """
        pass
