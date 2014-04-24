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

    Wavelet denoising

"""

from terapy.filters.base import Filter
import pywt
from statsmodels.robust import stand_mad
import numpy as np
import wx
from terapy.core import icon_path

class WaveletDenoise(Filter):
    """
    
        Wavelet denoising
    
    """
    __extname__ = "Wavelet denoising"
    dim = 1
    def __init__(self):
        Filter.__init__(self)
        self.wl_filter_list = []
        self.wl_filter_code = []
        self.threshold = 0.1
        self.auto_threshold = True
        for x in pywt.wavelist():
            p = pywt.Wavelet(x)
            self.wl_filter_list.append(p.family_name + " " + str(p.number))
            self.wl_filter_code.append(p.name)
        self.type = 'bior6.8'
        self.thresholding = 0
        self.config = ["threshold","auto_threshold","type","thresholding"]

    def apply_filter(self, array):
        if len(array.shape)!=1:
            return False
        mlv = pywt.dwt_max_level(array.shape[0],pywt.Wavelet(self.type))
        coeffs = pywt.wavedec(array.data, self.type, level=mlv, mode='per')
        if self.auto_threshold:
            sigma = stand_mad(coeffs[-1])
            uthresh = sigma*np.sqrt(2*np.log(len(coeffs)))
            self.threshold = uthresh
        else:
            uthresh = self.threshold
        denoised = coeffs[:]
        if self.thresholding==0: # Hard thresholding
            denoised[1:] = (pywt.thresholding.hard(i, value=uthresh) for i in denoised[1:])
        elif self.thresholding==1: # Soft thresholding
            denoised[1:] = (pywt.thresholding.soft(i, value=uthresh) for i in denoised[1:])
        signal = pywt.waverec(denoised, self.type, mode='per')
        array.data = signal[0:array.shape[0]]
        return True

    def set_filter(self, parent = None):
        dlg = WaveletSelectionDialog(parent, wlist = self.wl_filter_list, sel = self.wl_filter_code.index(self.type), thresh = self.thresholding, atr = self.auto_threshold, trval = self.threshold)
        if dlg.ShowModal() == wx.ID_OK:
            tp, self.thresholding, self.auto_threshold, self.threshold = dlg.GetValue()
            self.type = self.wl_filter_code[tp]
            dlg.Destroy()
            return True
        else:
            dlg.Destroy()
            return False

    def get_icon(self):
        return wx.Image(icon_path + "filter-denoise.png").ConvertToBitmap()

class WaveletSelectionDialog(wx.Dialog):
    def __init__(self, parent = None, title="Wavelet denoising", wlist = [], sel = 0, thresh=0, atr = True, trval = 0.1):
        wx.Dialog.__init__(self, parent, title=title)
        self.label_wavelet = wx.StaticText(self, -1, "Wavelets")
        self.choice_wavelet = wx.Choice(self, -1, choices=wlist)
        self.label_thresholding = wx.StaticText(self, -1, "Thresholding")
        self.choice_thresholding = wx.Choice(self, -1, choices=['Hard','Soft'])
        self.check_threshold = wx.CheckBox(self, -1, "Automatic threshold")
        self.label_threshold = wx.StaticText(self, -1, "Threshold value")
        self.input_threshold = wx.TextCtrl(self, -1, str(trval))
        self.button_OK = wx.Button(self, wx.ID_OK)
        self.button_Cancel = wx.Button(self, wx.ID_CANCEL)
        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.AddStretchSpacer(1)
        hbox.Add(self.button_Cancel, 0, wx.RIGHT|wx.ALIGN_RIGHT, 5)
        hbox.Add(self.button_OK, 0, wx.RIGHT|wx.ALIGN_RIGHT, 5)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.label_wavelet, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.choice_wavelet, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.label_thresholding, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.choice_thresholding, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.check_threshold, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.label_threshold, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.input_threshold, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(hbox, 0, wx.ALL|wx.EXPAND, 2)
        self.SetSizer(sizer)
        self.Fit()
        self.choice_wavelet.SetSelection(sel)
        self.choice_thresholding.SetSelection(thresh)
        self.label_threshold.Enable(not(atr))
        self.input_threshold.Enable(not(atr))
        self.check_threshold.SetValue(atr)

        self.Bind(wx.EVT_CHECKBOX, self.onAutoThreshold, self.check_threshold)
    
    def onAutoThreshold(self, event = None):
        self.auto_threshold = self.check_threshold.GetValue()
        self.label_threshold.Enable(not(self.auto_threshold))
        self.input_threshold.Enable(not(self.auto_threshold))
        
    def GetValue(self):
        return self.choice_wavelet.GetSelection(), self.choice_thresholding.GetSelection(), self.check_threshold.GetValue(), float(self.input_threshold.GetValue())
