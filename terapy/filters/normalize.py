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

    Normalize with reference

"""

from terapy.filters.base import Filter
from scipy.interpolate import interp1d
import wx
from terapy.core import icon_path
from wx.lib.pubsub import setupkwargs
from wx.lib.pubsub import pub
 
class Normalize(Filter):
    """
    
        Normalize with reference
    
    """
    __extname__ = "Normalize with reference"
    dim = 1
    def __init__(self):
        Filter.__init__(self)
        self.ref = None
        self.source = None
        self.arrays = []
        self.is_reference = True
        self.imethod = 1
        self.methods = ["nearest","linear","quadratic","cubic"]
        self.config = ["imethod"]
        pub.subscribe(self.set_arrays, "history.arrays")

    def apply_filter(self, array):
        if len(array.shape)!=1 or self.ref==None:
            return False
        i1d = interp1d(array.coords[0],array.data,kind=self.methods[self.imethod],bounds_error=False,fill_value=0.0)
        array.coords[0] = self.ref.coords[0]
        array.data = i1d(self.ref.coords[0])/self.ref.data
        array.shape = self.ref.shape
        return True
        
    def set_filter(self, parent = None):
        # need parent with history object providing several functions (see core.history for details)
        pub.sendMessage("request_arrays")
        reflist = [x for x in self.arrays if len(x.shape)==1]
        if len(reflist)==0:
            return False
        refnames = [x.name for x in reflist]
        if reflist.count(self.source)>0:
            idp = reflist.index(self.source)
        else:
            idp = 0
        dlg = ReferenceSelectionDialog(parent, reflist=refnames, sel = idp, isel = self.imethod)
        if dlg.ShowModal() == wx.ID_OK:
            idp, imethod = dlg.GetValue()
            if idp>-1:
                self.imethod = imethod
                dlg.Destroy()
                self.source = reflist[idp]
                pub.sendMessage("filter.change_reference",inst=self.arrays.index(self.source))
                return True
            else:
                dlg.Destroy()
                return False
        else:
            dlg.Destroy()
            return False
    
    def set_arrays(self, inst):
        # needed to pick up possible reference data arrays
        self.arrays = inst
    
    def get_icon(self):
        return wx.Image(icon_path + "filter-normalize.png").ConvertToBitmap()

class ReferenceSelectionDialog(wx.Dialog):
    def __init__(self, parent = None, title="Reference measurement", reflist = [], sel = 0, isel = 1):
        wx.Dialog.__init__(self, parent, title=title)
        self.label_reference = wx.StaticText(self, -1, "Reference scan")
        self.choice_reference = wx.Choice(self, -1, choices=reflist)
        self.label_interp = wx.StaticText(self, -1, "Interpolation method")
        self.choice_interp = wx.Choice(self, -1, choices=["Nearest neighbour", "Linear", "Quadratic spline", "Cubic spline"])
        self.button_OK = wx.Button(self, wx.ID_OK)
        self.button_Cancel = wx.Button(self, wx.ID_CANCEL)
        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.AddStretchSpacer(1)
        hbox.Add(self.button_Cancel, 0, wx.RIGHT|wx.ALIGN_RIGHT, 5)
        hbox.Add(self.button_OK, 0, wx.RIGHT|wx.ALIGN_RIGHT, 5)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.label_reference, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.choice_reference, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.label_interp, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.choice_interp, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(hbox, 0, wx.ALL|wx.EXPAND, 2)
        self.SetSizer(sizer)
        self.Fit()
        if sel>-1:
            self.choice_reference.SetSelection(sel)
        else:
            self.choice_reference.SetSelection(0)
        
        self.choice_interp.SetSelection(isel)
    
    def GetValue(self):
        return self.choice_reference.GetSelection(), self.choice_interp.GetSelection()
