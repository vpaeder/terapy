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

    Zero padding

"""

from terapy.filters.base import Filter
import numpy
import wx
from terapy.core import icon_path

class ZeroPadding(Filter):
    """
    
        Zero padding
    
    """
    __extname__ = "Zero padding"
    dim = 1
    def __init__(self):
        Filter.__init__(self)
    
    def apply_filter(self, array):
        if len(array.shape)!=1:
            return False
        # zero-padding to power-of-2 length
        nw = 2**numpy.ceil(numpy.log2(array.shape[0]))
        dw = nw-array.shape[0]
        dx = array.coords[0][1]-array.coords[0][0]
        if dw>1:
            nm = numpy.floor(dw/2)
            np = numpy.ceil(dw/2)
            array.data = numpy.concatenate((numpy.zeros(nm), array.data, numpy.zeros(np)))
            array.coords[0] = numpy.concatenate((numpy.arange(-dx*nm,0,dx)+min(array.coords[0]), array.coords[0], numpy.arange(dx,dx*(np+1),dx)+max(array.coords[0])))
        elif dw==1:
            array.data = numpy.concatenate((array.data,[0]))
            array.coords[0] = numpy.concatenate((array.coords[0], [dx+max(array.coords[0])]))
            
        return True

    def get_icon(self):
        return wx.Image(icon_path + "filter-zeropadding.png").ConvertToBitmap()
