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

    High pass filter

"""

from terapy.filters.base import Filter
from terapy.core.dataman import DataArray
from terapy.filters.apodization import ApodizationWindow
from terapy.filters.lowpass import BandpassFilterSelectionDialog
import numpy as np
import wx
from terapy.core import icon_path

class HighPass(Filter):
    """
    
        High pass filter
    
    """
    __extname__ = "High-pass filter"
    dim = 1
    def __init__(self):
        Filter.__init__(self)
        self.window = ApodizationWindow()
        self.window_list = self.window.window_list
        self.custom = 'np.exp(-4*x**2)'
        self.type = 0
        self.size = 11.0
        self.relative = True
        self.position = 25.0
        self.is_pre_filter = True
        self.config = ["custom","type","size","relative","position"]
    
    def apply_filter(self, array):
        if len(array.shape)!=1:
            return False
        
        # High-pass filter 
        p0 = min([np.floor(self.size/100.0*array.shape[0]), np.floor(array.shape[0]/2)])
        # compute window 
        wnd = DataArray(shape=[2*p0])
        wnd.data = np.ones(2*p0)
        self.window.apply_filter(wnd)
        # take left half
        wnd.data[p0:] = max(wnd.data)
        # compute how much to add
        shp = max([0,array.shape[0]-2*p0])
        if self.relative:
            # find max amplitude
            p1 = array.data.argmax()
        else:
            # take position from config
            p1 = np.floor((1.0-self.position/100.0)*array.shape[0])
        
        if p1<p0:
            fct = np.concatenate((wnd.data,max(wnd.data)*np.ones(shp)))
        elif p1+p0>array.shape[0]:
            fct = np.concatenate((max(wnd.data)*np.zeros(shp),wnd.data))
        else:
            fct = np.concatenate((np.zeros(array.shape[0]-p1-p0),wnd.data,np.ones(p1-p0)*max(wnd.data)))
        
        array.data = array.data*fct
        return True

    def set_filter(self, parent = None):
        dlg = BandpassFilterSelectionDialog(parent, title="High-pass filter window", wlist = self.window_list, sel = self.type, custom = self.custom, sz = self.size, relative = self.relative, position = self.position)
        if dlg.ShowModal() == wx.ID_OK:
            self.type, self.custom, self.size, self.relative, self.position = dlg.GetValue()
            self.window.type = self.type
            self.window.custom = self.custom
            dlg.Destroy()
            return True
        else:
            dlg.Destroy()
            return False

    def get_icon(self):
        return wx.Image(icon_path + "filter-hipass.png").ConvertToBitmap()
