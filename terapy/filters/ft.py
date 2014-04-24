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

    Fourier transform

"""

from terapy.filters.base import Filter
from scipy.fftpack import fft as fft 
import numpy as np
import wx
from terapy.core import icon_path

class FourierTransform(Filter):
    """
    
        Fourier transform
    
    """
    __extname__ = "Fourier transform"
    dim = 1
    def __init__(self):
        Filter.__init__(self)
        self.is_transform = True
        self.output_names = ["Complex (full spectrum)","Amplitude","Phase","Real","Imaginary"]
        self.output_qty = 1 # by default, return amplitude
        self.config = ["output_qty"]
    
    def apply_filter(self, array):
        if len(array.shape)!=1:
            return False
        # make frequency axis
        df  = 1/abs(array.coords[0][-1] - array.coords[0][0])    # time is stored in ps -> 1/ps = THz
        data_f = np.linspace(0, df*(array.shape[0]-1), array.shape[0])
        # calculate spectrum 
        if self.output_qty==0:
            data_s = fft(array.data)*(array.coords[0][1]-array.coords[0][0]) # complex-valued
        elif self.output_qty==1:
            data_s = abs(fft(array.data))*(array.coords[0][1]-array.coords[0][0])
        elif self.output_qty==2:
            ft = fft(array.data)
            data_s = np.arctan2(ft.imag,ft.real)
        elif self.output_qty==3:
            data_s = fft(array.data).real*(array.coords[0][1]-array.coords[0][0])
        elif self.output_qty==4:
            data_s = fft(array.data).imag*(array.coords[0][1]-array.coords[0][0])
        
        array.coords[0] = data_f[:len(data_f)/2-1]
        array.data = data_s[:len(data_f)/2-1]
        array.shape = array.data.shape
        return True

    def get_units(self, units):
        if len(units)!=2: return [1,1]
        if self.output_qty==2:
            from terapy.core.axedit import urg
            return [1/units[0], urg["rad"]]
        else:
            return [1/units[0], units[1]*units[0]]

    def set_filter(self, parent = None):
        dlg = FourierTransformSelectionDialog(parent, title="Fourier transform", output_names = self.output_names, output_qty = self.output_qty)
        if dlg.ShowModal() == wx.ID_OK:
            self.output_qty = dlg.GetValue()
            dlg.Destroy()
            return True
        else:
            dlg.Destroy()
            return False

    def get_icon(self):
        return wx.Image(icon_path + "filter-transform.png").ConvertToBitmap()

class FourierTransformSelectionDialog(wx.Dialog):
    def __init__(self, parent = None, title="Fourier transform", output_names = [], output_qty = 0):
        wx.Dialog.__init__(self, parent, title=title)
        self.label_output = wx.StaticText(self, -1, "Computed value")
        self.choice_output = wx.Choice(self, -1, choices=output_names)
        self.choice_output.SetSelection(output_qty)
        self.button_OK = wx.Button(self, wx.ID_OK)
        self.button_Cancel = wx.Button(self, wx.ID_CANCEL)
        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.AddStretchSpacer(1)
        hbox.Add(self.button_Cancel, 0, wx.RIGHT|wx.ALIGN_RIGHT, 5)
        hbox.Add(self.button_OK, 0, wx.RIGHT|wx.ALIGN_RIGHT, 5)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.label_output, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.choice_output, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(hbox, 0, wx.ALL|wx.EXPAND, 2)
        self.SetSizer(sizer)
        self.Fit()
    
    def GetValue(self):
        return self.choice_output.GetSelection()
