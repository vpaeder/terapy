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

    Generic device driver class.

"""

class Device():
    """
    
        Generic device driver class.
    
    """
    def __init__(self):
        """
        
            Pre-load device driver.
        
        """
        self.units = []
        self.config = []
    
    def assign(self, *args, **kwargs):
        """
        
            Configure device driver prior to initialization.
            
            Parameters:
                **kwargs    -    keyworded values corresponding to relevant configuration entries.
        
        """
        for name, value in kwargs.items():
            if hasattr(self,name):
                setattr(self,name,value)
        
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

    def xml2config(self, xmldom):
        """
        
            Read configuration from XML data.
            
            Parameters:
                xmldom    -    minidom XML document
        
        """
        for x in xmldom:
            if hasattr(x,'tagName'):
                if x.tagName == 'property':
                    k = x.attributes.keys()[0]
                    if hasattr(self,k):
                        v = getattr(self,k)
                        t = type(v)
                        try:
                            setattr(self,k,t(x.attributes[k].value))
                        except:
                            pass
    
    def widget(self,parent=None):
        """
        
            Return widget for graphical device control.
            
            Parameters:
                parent    -    parent window (wx.Window)
            
            Output:
                widget (wx.Frame)
        
        """
        # give a control widget to be added to the interface
        return None # if exists, should return a list of widgets (panels, frames or windows)
    
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

