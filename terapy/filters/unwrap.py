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

    Phase unwrapping

"""

from terapy.filters.base import Filter
import numpy as np
import wx
from terapy.core import icon_path

class PhaseUnwrapping(Filter):
    """
    
        Phase unwrapping
    
    """
    __extname__ = "Phase unwrapping"
    dim = 1
    def __init__(self):
        Filter.__init__(self)
        self.threshold = 1.0 # unwrap threshold (in units of pi)
        self.config = ["threshold"]
    
    def apply_filter(self, array):
        if len(array.shape)!=1:
            return False
        
        if isinstance(array.data[0],complex):
            phase = np.arctan2(array.data.imag,array.data.real)
            array.data = abs(array.data)*np.exp(1j*np.unwrap(phase,np.pi*self.threshold))
        else:
            array.data = np.unwrap(np.array(array.data),np.pi*self.threshold)
        
        return True

    def get_units(self, units):
        if len(units)!=2: return [1,1]
        return [units[0], units[1]]

    def set_filter(self, parent = None):
        dlg = wx.TextEntryDialog(parent,message="Unwrap threshold (in units of pi)",defaultValue=str(self.threshold))
        if dlg.ShowModal() == wx.ID_OK:
            self.threshold = float(dlg.GetValue())
            dlg.Destroy()
            return True
        else:
            dlg.Destroy()
            return False

    def get_icon(self):
        return wx.Image(icon_path + "filter-unwrap.png").ConvertToBitmap()
