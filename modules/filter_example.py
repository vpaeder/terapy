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
    Post-processing filter example
"""

from terapy.filters.base import Filter

class FilterExample(Filter):
    """
        Explain here what the filter does.
        
        Properties:
            __extname__    -    long name (str)
            dim            -    dimension of data that this filter can treat (int)
    """
    __extname__ = "Do nothing"
    dim = 1
    def __init__(self):
        """
            Initialization.
        """
        Filter.__init__(self)
        # Insert here what should be done when the filter instance is created
        # This will be executed only once
        self.is_pre_filter = False # set to True if this filter can be applied before a transform (e.g. windowing)
        self.is_transform = False # set to True if this filter is a transform (Fourier or something else)
        self.is_reference = False # set to True if this filter sets a reference
        self.is_active = True # set to True if this filter is active
        self.is_visible = True # set to True if this filter is visible in the menu
        self.config = ['is_visible'] # list of variables to be saved in external config file

    def apply_filter(self, array):
        """
            Apply filter to given array.
            Parameters:
                array    -    data array (DataArray)
        """
        # Insert here what the filter should do on data
        return True
    
    def set_filter(self, parent = None):
        """
            Set filter properties.
            Parameters:
                parent    -    parent window (wx.Window)
            Output:
                True (success) / False (failure/cancellation)
        """
        # Insert here what should be done when the filter properties are requested to be changed
        # e.g. open a property dialog or compute something
        # return True if the action is successful, False otherwise 
        return True

    def get_icon(self):
        """
            Return filter icon.
            Output:
                16x16 icon (wx.Bitmap)
        """
        import wx
        from terapy.core import icon_path
        # Place your custom icon where needed and change the path accordingly
        return wx.Image(icon_path + "empty.png").ConvertToBitmap()
