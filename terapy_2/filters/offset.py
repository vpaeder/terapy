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

    Offset correction

"""

from terapy.filters.base import Filter
import wx
from numpy import mean
from terapy.core import icon_path

class Offset(Filter):
    """
    
        Offset correction
    
    """
    __extname__ = "Offset correction"
    dim = 1
    def __init__(self):
        Filter.__init__(self)
        self.position = 3.0
        self.width = 0.1
        self.config = ["position","width"]

    def apply_filter(self, array):
        if len(array.shape)!=1:
            return False
        pmin = abs(array.data).argmax()
        dx = array.coords[0][1]-array.coords[0][0] # assume uniform sampling
        pmin = pmin - int(self.position/dx + self.width/2.0/dx)
        if pmin<0:
            pmin = 0
        
        pmax = pmin + 1 + int(self.width/dx)
        
        avg = mean(array.data[pmin:pmax])
        array.data = array.data - avg
        return True
    
    def set_filter(self, parent = None):
        dlg = OffsetDialog(parent,position=self.position, width = self.width)
        if dlg.ShowModal() == wx.ID_OK:
            self.position, self.width = dlg.GetValue()
            dlg.Destroy()
            return True
        else:
            dlg.Destroy()
            return False

    def get_icon(self):
        return wx.Image(icon_path + "filter-offset.png").ConvertToBitmap()
        
class OffsetDialog(wx.Dialog):
    def __init__(self, parent = None, title="Offset correction", position = 0.0, width = 0.1):
        wx.Dialog.__init__(self, parent, title=title)
        self.label_position = wx.StaticText(self, -1, "Distance before main peak (ps)")
        self.input_position = wx.TextCtrl(self, -1, str(position))
        self.label_width = wx.StaticText(self, -1, "Averaging width (ps)")
        self.input_width = wx.TextCtrl(self, -1, str(width))
        self.button_OK = wx.Button(self, wx.ID_OK)
        self.button_Cancel = wx.Button(self, wx.ID_CANCEL)
        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.AddStretchSpacer(1)
        hbox.Add(self.button_Cancel, 0, wx.RIGHT|wx.ALIGN_RIGHT, 5)
        hbox.Add(self.button_OK, 0, wx.RIGHT|wx.ALIGN_RIGHT, 5)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.label_position, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.input_position, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.label_width, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.input_width, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(hbox, 0, wx.ALL|wx.EXPAND, 2)
        self.SetSizer(sizer)
        self.Fit()
    
    def GetValue(self):
        return float(self.input_position.GetValue()), float(self.input_width.GetValue())
