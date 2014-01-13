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

    Apodization window

"""

from terapy.filters.base import Filter
import numpy as np
import wx
from terapy.core import icon_path

class ApodizationWindow(Filter):
    """
    
        Apodization window
    
    """
    __extname__ = "Apodization window"
    dim = 1
    def __init__(self):
        Filter.__init__(self)
        self.window_list = ["Boxcar","Bartlett","Blackman","Hamming","Hanning","Blackman-Harris","Lanczos","Custom..."]
        self.custom = 'np.exp(-4*x**2)'
        self.type = 0
        self.is_pre_filter = True
        self.config = ["custom","type"]
        
    def apply_filter(self, array):
        if len(array.shape)!=1:
            return False # need 2D data
        nx = array.shape[0]
        # Apodization function
        if self.type == 1:
            ft = np.bartlett(nx)
        elif self.type == 2:
            ft = np.blackman(nx)
        elif self.type == 3:
            ft = np.hamming(nx)
        elif self.type == 4:
            ft = np.hanning(nx)
        elif self.type == 5:
            # Blackman-Harris window
            a0 = 0.35875
            a1 = 0.48829
            a2 = 0.14128
            a3 = 0.01168
            x = np.linspace(0,1,nx)
            ft = a0 - a1*np.cos(2*np.pi*x) + a2*np.cos(4*np.pi*x) + a3*np.cos(6*np.pi*x) 
        elif self.type == 6:
            # Lanczos window
            x = np.linspace(-1,1,nx)
            ft = np.sinc(x)
        elif self.type == 7:
            x = np.linspace(-1,1,nx)
            exec('x='+self.custom)
            ft = x
        else:
            ft = np.ones(nx)
        
        array.data = array.data*ft
        return True
    
    def set_filter(self, parent = None):
        dlg = WindowSelectionDialog(parent, wlist = self.window_list, sel = self.type, custom = self.custom)
        if dlg.ShowModal() == wx.ID_OK:
            self.type, self.custom = dlg.GetValue()
            dlg.Destroy()
            return True
        else:
            dlg.Destroy()
            return False

    def get_icon(self):
        return wx.Image(icon_path + "filter-window.png").ConvertToBitmap()

class WindowSelectionDialog(wx.Dialog):
    def __init__(self, parent = None, title="Apodization window", wlist = [], sel = 0, custom = ""):
        wx.Dialog.__init__(self, parent, title=title)
        self.label_window = wx.StaticText(self, -1, "Window function")
        self.choice_window = wx.Choice(self, -1, choices=wlist)
        self.label_custom = wx.StaticText(self, -1, "y = f(x) defined on (-1,1):")
        self.input_custom = wx.TextCtrl(self, -1, custom)
        self.button_OK = wx.Button(self, wx.ID_OK)
        self.button_Cancel = wx.Button(self, wx.ID_CANCEL)
        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.AddStretchSpacer(1)
        hbox.Add(self.button_Cancel, 0, wx.RIGHT|wx.ALIGN_RIGHT, 5)
        hbox.Add(self.button_OK, 0, wx.RIGHT|wx.ALIGN_RIGHT, 5)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.label_window, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.choice_window, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.label_custom, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.input_custom, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(hbox, 0, wx.ALL|wx.EXPAND, 2)
        self.SetSizer(sizer)
        self.Fit()
        self.choice_window.SetSelection(sel)
        if sel<len(wlist)-1:
            self.label_custom.Enable(False)
            self.input_custom.Enable(False)
        
        self.Bind(wx.EVT_CHOICE, self.onWindowSelect, self.choice_window)
    
    def onWindowSelect(self, event = None):
        state = (self.choice_window.GetSelection()==self.choice_window.GetCount()-1)
        self.label_custom.Enable(state)
        self.input_custom.Enable(state)
    
    def GetValue(self):
        return self.choice_window.GetSelection(), self.input_custom.GetValue()
