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

    Low pass filter

"""

from terapy.filters.base import Filter
from terapy.core.dataman import DataArray
from terapy.filters.apodization import ApodizationWindow
import numpy as np
import wx
from terapy.core import icon_path

class LowPass(Filter):
    """
    
        Low pass filter
    
    """
    __extname__ = "Low-pass filter"
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
        # Low-pass filter 
        p0 = min([np.floor(self.size/100.0*array.shape[0]), np.floor(array.shape[0]/2)])
        # compute window 
        wnd = DataArray(shape=[2*p0])
        wnd.data = np.ones(2*p0)
        self.window.apply_filter(wnd)
        # take right half
        wnd.data[:p0] = max(wnd.data)
        # compute how much to add
        shp = max([0,array.shape[0]-2*p0])
        if self.relative:
            # find max amplitude
            p1 = array.data.argmax()
        else:
            # take position from config
            p1 = np.floor(self.position/100.0*array.shape[0])
        
        if p1<p0:
            fct = np.concatenate((wnd.data,np.zeros(shp)))
        elif p1+p0>array.shape[0]:
            fct = np.concatenate((max(wnd.data)*np.ones(shp),wnd.data))
        else:
            fct = np.concatenate((np.ones(p1-p0)*max(wnd.data),wnd.data,np.zeros(array.shape[0]-p1-p0)))
        
        array.data = array.data*fct
        return True
    
    def set_filter(self, parent = None):
        dlg = BandpassFilterSelectionDialog(parent, title="Low-pass filter window", wlist = self.window_list, sel = self.type, custom = self.custom, sz = self.size, relative = self.relative, position = self.position)
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
        return wx.Image(icon_path + "filter-lopass.png").ConvertToBitmap()

class BandpassFilterSelectionDialog(wx.Dialog):
    def __init__(self, parent = None, title="", wlist = [], sel = 0, custom = "", sz = 0, relative = True, position = 25):
        wx.Dialog.__init__(self, parent, title=title)
        self.label_window = wx.StaticText(self, -1, "Window function")
        self.choice_window = wx.Choice(self, -1, choices=wlist)
        self.label_custom = wx.StaticText(self, -1, "y = f(x) defined on (-1,1):")
        self.input_custom = wx.TextCtrl(self, -1, custom)
        self.label_size = wx.StaticText(self, -1, "Size (%)")
        self.input_size = wx.TextCtrl(self, -1, str(sz))
        self.check_relative = wx.CheckBox(self, -1, "Relative to max. amplitude")
        self.label_position = wx.StaticText(self, -1, "Position (%)")
        self.input_position = wx.TextCtrl(self, -1, str(position))
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
        sizer.Add(self.label_size, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.input_size, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.check_relative, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.label_position, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.input_position, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(hbox, 0, wx.ALL|wx.EXPAND, 2)
        self.SetSizer(sizer)
        self.Fit()
        self.choice_window.SetSelection(sel)
        if sel<len(wlist)-1:
            self.label_custom.Enable(False)
            self.input_custom.Enable(False)
        
        self.check_relative.SetValue(relative)
        if relative:
            self.label_position.Enable(False)
            self.input_position.Enable(False)
            
        self.Bind(wx.EVT_CHOICE, self.onWindowSelect, self.choice_window)
        self.Bind(wx.EVT_TEXT_ENTER, self.onSizeChange, self.input_size)
        self.Bind(wx.EVT_CHECKBOX, self.onRelativeCheck, self.check_relative)
        self.Bind(wx.EVT_TEXT_ENTER, self.onPositionChange, self.input_position)
    
    def onWindowSelect(self, event = None):
        state = (self.choice_window.GetSelection()==self.choice_window.GetCount()-1)
        self.label_custom.Enable(state)
        self.input_custom.Enable(state)
    
    def onSizeChange(self, event = None):
        vl = float(self.input_size.GetValue())
        if vl<0:
            self.input_size.SetValue("0.0")
        elif vl>50:
            self.input_size.SetValue("50.0")
    
    def onRelativeCheck(self, event = None):
        state = not(self.check_relative.GetValue())
        self.label_position.Enable(state)
        self.input_position.Enable(state)
    
    def onPositionChange(self, event = None):
        vl = float(self.input_size.GetValue())
        if vl<0:
            self.input_size.SetValue("0.0")
        elif vl>100:
            self.input_size.SetValue("100.0")
            
    def GetValue(self):
        return self.choice_window.GetSelection(), self.input_custom.GetValue(), float(self.input_size.GetValue()), self.check_relative.GetValue(), float(self.input_position.GetValue())
