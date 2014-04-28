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

    Savitzky-Golay smoothing
    Adapted from http://wiki.scipy.org/Cookbook/SavitzkyGolay

"""

from terapy.filters.base import Filter
import numpy as np
import wx
from terapy.core import icon_path

class SavitzkyGolay(Filter):
    """
    
        Savitzky-Golay smoothing
        Adapted from http://wiki.scipy.org/Cookbook/SavitzkyGolay
    
    """
    __extname__ = "Savitzky-Golay smoothing"
    dim = 1
    def __init__(self):
        Filter.__init__(self)
        self.size = 11
        self.order = 5
        self.deriv = 0
        self.rate = 1
        self.config = ["size","order"]

    def apply_filter(self, array):
        if len(array.shape)!=1:
            return False
        # from SciPy cookbook http://wiki.scipy.org/Cookbook/SavitzkyGolay
        from math import factorial
        try:
            self.size = np.abs(np.int(self.size))
            self.order = np.abs(np.int(self.order))
        except ValueError:
            raise ValueError("self.size and self.order have to be of type int")
        if self.size % 2 != 1 or self.size < 1:
            raise TypeError("self.size size must be a positive odd number")
        if self.size < self.order + 2:
            raise TypeError("self.size is too small for the polynomial order")
        order_range = range(self.order+1)
        half_window = (self.size -1) // 2
        # precompute coefficients
        b = np.mat([[k**i for i in order_range] for k in range(-half_window, half_window+1)])
        m = np.linalg.pinv(b).A[self.deriv] * self.rate**self.deriv * factorial(self.deriv)
        # pad the signal at the extremes with
        # values taken from the signal itself
        firstvals = array.data[0] - np.abs( array.data[1:half_window+1][::-1] - array.data[0] )
        lastvals = array.data[-1] + np.abs(array.data[-half_window-1:-1][::-1] - array.data[-1])
        data_y = np.concatenate((firstvals, array.data, lastvals))
        array.data = np.convolve( m[::-1], data_y, mode='valid')
        return True
    
    def set_filter(self, parent = None):
        dlg = SGSmoothingSelectionDialog(parent, title = "Savitzky-Golay smoothing", sz = self.size, order = self.order)
        if dlg.ShowModal() == wx.ID_OK:
            self.size, self.order = dlg.GetValue()
            dlg.Destroy()
            return True
        else:
            dlg.Destroy()
            return False

    def get_icon(self):
        return wx.Image(icon_path + "filter-denoise.png").ConvertToBitmap()

class SGSmoothingSelectionDialog(wx.Dialog):
    def __init__(self, parent = None, title="Savitzky-Golay smoothing", sz = 11, order = 5):
        wx.Dialog.__init__(self, parent, title=title)
        self.label_size = wx.StaticText(self, -1, "Window size")
        self.input_size = wx.TextCtrl(self, -1, str(sz), style=wx.TE_PROCESS_ENTER)
        self.label_order = wx.StaticText(self, -1, "Polynomial order")
        self.input_order = wx.TextCtrl(self, -1, str(order), style=wx.TE_PROCESS_ENTER)
        self.button_OK = wx.Button(self, wx.ID_OK)
        self.button_Cancel = wx.Button(self, wx.ID_CANCEL)
        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.AddStretchSpacer(1)
        hbox.Add(self.button_Cancel, 0, wx.RIGHT|wx.ALIGN_RIGHT, 5)
        hbox.Add(self.button_OK, 0, wx.RIGHT|wx.ALIGN_RIGHT, 5)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.label_size, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.input_size, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.label_order, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.input_order, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(hbox, 0, wx.ALL|wx.EXPAND, 2)
        self.SetSizer(sizer)
        self.Fit()
        
        self.Bind(wx.EVT_TEXT_ENTER, self.OnFilterChange, self.input_size)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnFilterChange, self.input_order)
        self.input_size.Bind(wx.EVT_KILL_FOCUS, self.OnFilterChange)
        self.input_order.Bind(wx.EVT_KILL_FOCUS, self.OnFilterChange)
    
    def OnFilterChange(self, event = None):
        sg_size = int(self.input_size.GetValue())
        sg_order = int(self.input_order.GetValue())
        if sg_size%2==0:
            sg_size = sg_size + 1
        if sg_size<1:
            sg_size = 1
        if sg_order>sg_size-1:
            sg_order = sg_size-1
        if sg_order<1:
            sg_order = 1
        self.input_size.SetValue(str(sg_size))
        self.input_order.SetValue(str(sg_order))
        event.Skip()
    
    def GetValue(self):
        return int(self.input_size.GetValue()), int(self.input_order.GetValue())
