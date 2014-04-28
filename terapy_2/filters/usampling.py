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

    Uniform resampling

"""

from terapy.filters.base import Filter
import numpy as np
from scipy.interpolate import interp1d
import wx
from terapy.core import icon_path

class UniformSampling(Filter):
    """
    
        Uniform resampling
    
    """
    __extname__ = "Uniform sampling"
    dim = 1
    def __init__(self):
        Filter.__init__(self)
        self.imethod = 1
        self.methods = ["nearest","linear","quadratic","cubic"]
        self.config = ["imethod"]
    
    def apply_filter(self, array):
        if len(array.shape)!=1:
            return False
        
        s = array.coords[0].argsort()
        array.coords[0] = array.coords[0][s]
        array.data = array.data[s]
        
        data_xi = np.linspace(array.coords[0].min(),array.coords[0].max(),array.shape[0])
        
        i1d = interp1d(array.coords[0],array.data,kind=self.methods[self.imethod],bounds_error=False,fill_value=0.0)
        array.data = i1d(data_xi)
        array.coords[0] = data_xi
        return True

    def set_filter(self, parent = None):
        dlg = ResamplingSelectionDialog(parent, sel = self.imethod)
        if dlg.ShowModal() == wx.ID_OK:
            self.imethod = dlg.GetValue()
            dlg.Destroy()
            return True
        else:
            dlg.Destroy()
            return False
        
    def get_icon(self):
        return wx.Image(icon_path + "filter-uniform.png").ConvertToBitmap()

class ResamplingSelectionDialog(wx.Dialog):
    def __init__(self, parent = None, title="Interpolation method", sel = 1):
        wx.Dialog.__init__(self, parent, title=title)
        self.choice_interp = wx.Choice(self, -1, choices=["Nearest neighbour", "Linear", "Quadratic spline", "Cubic spline"])
        self.button_OK = wx.Button(self, wx.ID_OK)
        self.button_Cancel = wx.Button(self, wx.ID_CANCEL)
        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.AddStretchSpacer(1)
        hbox.Add(self.button_Cancel, 0, wx.RIGHT|wx.ALIGN_RIGHT, 5)
        hbox.Add(self.button_OK, 0, wx.RIGHT|wx.ALIGN_RIGHT, 5)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.choice_interp, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(hbox, 0, wx.ALL|wx.EXPAND, 2)
        self.SetSizer(sizer)
        self.Fit()
        self.choice_interp.SetSelection(sel)
        
    def GetValue(self):
        return self.choice_interp.GetSelection()
		