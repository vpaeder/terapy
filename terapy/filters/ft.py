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

    Fourier transform

"""

from terapy.filters.base import Filter
from scipy.fftpack import fft as fft 
import numpy as np
import wx
from terapy.core import icon_path

class FourierTransform(Filter):
    """
    
        Fourier transform
    
    """
    __extname__ = "Fourier transform"
    dim = 1
    def __init__(self):
        Filter.__init__(self)
        self.is_transform = True
    
    def apply_filter(self, array):
        if len(array.shape)!=1:
            return False
        # make frequency axis
        df  = 1/abs(array.coords[0][-1] - array.coords[0][0])    # time is stored in ps -> 1/ps = THz
        data_f = np.linspace(0, df*(array.shape[0]-1), array.shape[0])
        # calculate spectrum 
        data_s = abs(fft(array.data))*(array.coords[0][1]-array.coords[0][0])
        
        array.coords[0] = data_f[:len(data_f)/2-1]
        array.data = data_s[:len(data_f)/2-1]
        array.shape = array.data.shape
        return True

    def get_units(self, units):
        if len(units)!=2: return [1,1]
        return [1/units[0], units[1]*units[0]]

    def get_icon(self):
        return wx.Image(icon_path + "filter-transform.png").ConvertToBitmap()
