#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2013  Vincent Paeder
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

    Generic post-processing filter class

"""

import wx
from terapy.core import icon_path

class Filter():
    """
    
        Generic post-processing filter class
        
        Properties:
            __extname__    -    long name (str)
            dim            -    dimension of data that this filter can treat (int)
    
    """
    __extname__ = "Generic filter"
    dim = -1
    def __init__(self):
        """
        
            Initialization.
        
        """
        self.is_pre_filter = False # if True, filter applies only before domain transform
        self.is_transform = False # if True, filter is domain transform
        self.is_reference = False # if True, filter is reference filter (e.g. normalization)
        self.is_active = True # if True, filter is active
        self.is_visible = True # if True, filter is visible in interface
        self.config = []
        self.name = self.__extname__
    
    def apply_filter(self, array):
        """
        
            Apply filter to given array.
            
            Parameters:
                array    -    data array (DataArray)
        
        """
        return True
    
    def set_filter(self, parent = None):
        """
        
            Set filter properties.
            
            Parameters:
                parent    -    parent window (wx.Window)
            
            Output:
                True (success) / False (failure/cancellation)
        
        """
        return True
    
    def get_units(self, units):
        """
        
            Compute units of array coordinates and data after processsing.
            
            Parameters:
                units    -    list of units (list of quantities)
            
            Output:
                list of units (list of quantities)
        
        """
        return units
    
    def get_icon(self):
        """
        
            Return filter icon.
            
            Output:
                16x16 icon (wx.Bitmap)
        
        """
        return wx.Image(icon_path + "empty.png").ConvertToBitmap()
