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

    Center maximum value by zero-padding

"""

from terapy.filters.base import Filter
import numpy as np
import wx
from terapy.core import icon_path

class Centering(Filter):
    """
    
        Center maximum value by zero-padding
    
    """
    __extname__ = "Center max value"
    dim = 1
    def __init__(self):
        Filter.__init__(self)
    
    def apply_filter(self, array):
        # re-center data with zero-padding
        if len(array.shape)!=1:
            return False
        
        data_y = array.data
        data_x = array.coords[0]
        pm = abs(data_y).argmax()
        if pm>len(data_y)/2:
            dx = data_x[1] - data_x[0]
            nz = 2*(pm - len(data_y)/2)
            data_y = np.concatenate((data_y, np.zeros(nz)))
            data_x = np.linspace(data_x.min(), data_x.max() + dx*nz, len(data_y))
        elif pm<len(data_y)/2:
            dx = data_x[1] - data_x[0]
            nz = 2*(len(data_y)/2 - pm)
            data_y = np.concatenate((np.zeros(nz), data_y))
            data_x = np.linspace(data_x.min() - dx*nz, data_x.max(), len(data_y))
        
        array.coords[0] = data_x
        array.data = data_y
        array.shape = data_y.shape
        return True

    def get_icon(self):
        return wx.Image(icon_path + "filter-center.png").ConvertToBitmap()
