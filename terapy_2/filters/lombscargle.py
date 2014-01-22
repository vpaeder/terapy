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

    Lomb-Scargle filter

"""

from terapy.filters.base import Filter
from scipy.signal import lombscargle 
import numpy as np
import wx
from terapy.core import icon_path

class LombScargle(Filter):
    """
    
        Lomb-Scargle filter
    
    """
    __extname__ = "Lomb-Scargle periodogram"
    dim = 1
    def __init__(self):
        Filter.__init__(self)
        self.is_transform = True
    
    def apply_filter(self, array):
        if len(array.shape)!=1:
            return False
        # make frequency axis
        df  = 1/abs(array.coords[0][-1] - array.coords[0][0])    # time is stored in ps -> 1/ps = THz
        my = max(abs(array.data))
        data_f = np.linspace(df/array.shape[0], df*(array.shape[0]-1)*np.pi, array.shape[0]) # Lomb-Scargle doesn't allow f=0
        #data_f = data_f[:len(data_f)/2-1] # return frequencies up to 1/dt/2 to be consistent with FFT (not compulsory)
        # calculate spectrum 
        data_s = abs(lombscargle(array.coords[0], array.data/my, data_f))*my**2
        array.coords[0] = data_f/(2*np.pi)
        array.data = data_s
        return True

    def get_units(self, units):
        if len(units)!=2: return [1,1]
        return [1/units[0], units[1]]
    
    def get_icon(self):
        return wx.Image(icon_path + "filter-transform.png").ConvertToBitmap()
