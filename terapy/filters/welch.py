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

    Welch periodogram

"""

from terapy.filters.base import Filter
from scipy.signal import welch 
import numpy as np
import wx
from terapy.core import icon_path

class Welch(Filter):
    """
    
        Welch periodogram
    
    """
    __extname__ = "Welch periodogram"
    dim = 1
    def __init__(self):
        Filter.__init__(self)
        self.window_list = ["Boxcar", "Triangular", "Blackman", "Hamming", "Hann", "Bartlett", "Flat top", "Parzen", "Bohman", "Blackman-Harris", "Nuttall", "Bartlett-Hann"]
        self.window_code = ["boxcar", "triang", "blackman", "hamming", "hann", "bartlett", "flattop", "parzen", "bohman", "blackmanharris", "nuttall", "barthann"]
        self.type = 0
        self.length = 20.0
        self.overlap = 50.0
        self.scaling = 0
        self.is_transform = True
        self.config = ["type","length","overlap","scaling"]
        
    def apply_filter(self, array):
        if len(array.shape)!=1:
            return False
        # make frequency axis
        fmax = 1/(array.coords[0][1] - array.coords[0][0])
        # calculate spectrum
        val_length = np.floor(self.length/100.0*array.shape[0])
        if val_length<1:
            val_length=1
        val_overlap = np.floor(val_length*self.overlap/100.0)
        
        a = welch(array.data,fs=fmax,window=self.window_code[self.type],nperseg=val_length,noverlap=val_overlap,scaling=['density','spectrum'][self.scaling])
        array.data = abs(a[1])
        array.coords[0] = a[0]
        array.shape[0] = len(array.data)
        return True
    
    def set_filter(self, parent = None):
        dlg = WelchSelectionDialog(parent, wlist = self.window_list, val_length=self.length, val_overlap=self.overlap, sel_window=self.type, sel_qty=self.scaling)
        if dlg.ShowModal() == wx.ID_OK:
            self.type, self.length, self.overlap, self.scaling = dlg.GetValue()
            dlg.Destroy()
            return True
        else:
            dlg.Destroy()
            return False

    def get_units(self, units):
        if len(units)!=2: return [1,1]
        return [1/units[0], units[1]]
    
    def get_icon(self):
        return wx.Image(icon_path + "filter-transform.png").ConvertToBitmap()

class WelchSelectionDialog(wx.Dialog):
    def __init__(self, parent = None, title="Welch periodogram", wlist=[], val_length=20, val_overlap=50, sel_window=0, sel_qty=0):
        wx.Dialog.__init__(self, parent, title=title)
        self.label_window = wx.StaticText(self, -1, "Window function")
        self.choice_window = wx.Choice(self, -1, choices=wlist)
        self.label_length = wx.StaticText(self, -1, "Segment length (%)")
        self.input_length = wx.TextCtrl(self, -1, str(val_length))
        self.label_overlap = wx.StaticText(self, -1, "Overlap (%)")
        self.input_overlap = wx.TextCtrl(self, -1, str(val_overlap))
        self.label_qty = wx.StaticText(self, -1, "Computed quantity")
        self.choice_qty = wx.Choice(self, -1, choices=["Spectral density","Power spectrum"])
        self.button_OK = wx.Button(self, wx.ID_OK)
        self.button_Cancel = wx.Button(self, wx.ID_CANCEL)
        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.AddStretchSpacer(1)
        hbox.Add(self.button_Cancel, 0, wx.RIGHT|wx.ALIGN_RIGHT, 5)
        hbox.Add(self.button_OK, 0, wx.RIGHT|wx.ALIGN_RIGHT, 5)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.label_window, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.choice_window, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.label_length, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.input_length, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.label_overlap, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.input_overlap, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.label_qty, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.choice_qty, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(hbox, 0, wx.ALL|wx.EXPAND, 2)
        self.SetSizer(sizer)
        self.Fit()
        self.choice_window.SetSelection(sel_window)
        self.choice_qty.SetSelection(sel_qty)
        
        self.Bind(wx.EVT_TEXT_ENTER, self.onChangeLength, self.input_length)
        self.Bind(wx.EVT_TEXT_ENTER, self.onChangeLength, self.input_overlap)
        self.input_length.Bind(wx.EVT_KILL_FOCUS, self.onChangeLength)
        self.input_overlap.Bind(wx.EVT_KILL_FOCUS, self.onChangeLength)
    
    def onChangeLength(self, event = None):
        val_length = float(self.input_length.GetValue())
        val_overlap = float(self.input_overlap.GetValue())
        if val_length<0:
            val_length=0
        if val_length>100:
            val_length=100
        
        if val_overlap>100:
            val_overlap = 100
        if val_overlap<0:
            val_overlap = 0
        
        self.input_length.SetValue(str(val_length))
        self.input_overlap.SetValue(str(val_overlap))
    
    def GetValue(self):
        return self.choice_window.GetSelection(), float(self.input_length.GetValue()), float(self.input_overlap.GetValue()), self.choice_qty.GetSelection()
