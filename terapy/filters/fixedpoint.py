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

    Fixed point iteration algorithm for refractive index extraction

"""

from terapy.filters.base import Filter
from scipy.interpolate import interp1d
from numpy import floor, unwrap, arctan2, pi, exp, log
import wx
from terapy.core import icon_path
from wx.lib.pubsub import setupkwargs
from wx.lib.pubsub import pub
 
class FixedPoint(Filter):
    """
    
        Fixed point iteration algorithm for refractive index extraction
    
    """
    __extname__ = "Fixed-point iteration"
    dim = 1
    def __init__(self):
        Filter.__init__(self)
        self.ref = None
        self.source = None
        self.arrays = []
        self.is_reference = True
        #self.is_visible = False
        self.thickness = 3000.0
        self.deviation = 2.0
        self.imethod = 1
        self.methods = ["nearest","linear","quadratic","cubic"]
        self.imaginary = False
        self.host = 1.0 # index of surrounding medium
        self.config = ["thickness","deviation","host","imaginary","imethod"]
        pub.subscribe(self.set_arrays, "history.arrays")

    def apply_filter(self, array):
        c = 299792458e6 # speed of light in um/s
        if len(array.shape)!=1 or self.ref==None:
            return False
        i1d = interp1d(array.coords[0],array.data,kind=self.methods[self.imethod],bounds_error=False,fill_value=0.0)
        array.coords[0] = self.ref.coords[0]
        array.data = i1d(self.ref.coords[0])
        omega = 2*pi*array.coords[0]*1e12
        
        # pick source data
        if array.source != None:
            trace = array.source
        else:
            trace = array
        
        # Initial estimate of RI from pulse delay
        t0 = self.source.coords[0][self.source.data.argmax()]
        t1 = trace.coords[0][trace.data.argmax()]
        dt = abs(t1-t0)*1e-12
        ns0 = c*dt/self.thickness + self.host # RI estimate
        tmax = (trace.coords[0][-1] - t0)*1e-12 # max delay after main pulse
        Nr = int(floor((c/(ns0*self.thickness)*tmax-1.0)/2.0)) # max number of echoes 
        
        # correct phase - obviously, the phase information is present only if the full complex signal is used
        ratio = array.data/self.ref.data
        phase = unwrap(-arctan2(ratio.imag,ratio.real))
        p0 = self.thickness/c*(ns0-self.host) # slope estimate
        for n in range(len(phase)-1):
            dp = (omega[n+1]-omega[n])*p0*self.deviation
            if abs(phase[n+1]-phase[n])>dp:
                phase[n+1:] = phase[n+1:] - phase[n+1] + phase[n] + dp 
        
        phase = phase - phase[0]
        
        # fixed-point iteration
        for n in range(len(phase)):
            ns = ns0
            ns1 = ns0 + self.host
            nit = 0
            while abs(ns1-ns)>1e-12:
                nit+=1
                ns1 = ns
                Fp = self.fabry_perot(self.host, ns, omega[n], self.thickness, Nr)
                Hm = ratio[n]/Fp
                Fpp = -arctan2(Fp.imag,Fp.real)
                cor = 4.0*ns/(ns+self.host)**2
                ns = c/(omega[n]*self.thickness)*(phase[n]-Fpp+arctan2(cor.imag,cor.real)) + self.host
                ks = -c/(omega[n]*self.thickness)*(log(abs(Hm))-log(abs(cor)))
                ns = abs(ns) - 1j*abs(ks)
                
                if nit>100: break # stop after 100 iterations
            
            if self.imaginary:
                array.data[n] = -ns.imag
            else:
                array.data[n] = ns.real
        
        array.shape = self.ref.shape
        return True
    
    def fabry_perot(self,n1,ns,om,L,Nmax):
        """
        
            Compute the contribution of Fabry-Pérot interferences in the transmission through a slab.
            
            Parameters:
                n1    -    refractive index of surrounding medium (complex)
                ns    -    refractive index of slab (complex)
                om    -    angular frequency (float)
                L     -    slab thickness in micrometers (float)
                Nmax  -    number of reflections to take into account (int)
            
            Output:
                FP contribution (complex) 
        
        """
        c = 299792458e6
        
        rsa = (ns-n1)/(n1+ns)
        ps = exp(-1j*2*ns*om/c*L)
        
        Emod = 0
        for nr in range(Nmax+1):
            Emod += (rsa**2*ps)**nr
        
        return Emod
    
    def estimated_transfer_function(self,n1,ns,om,L):
        """
        
            Compute the one-pass transfer function through a slab. 
            
            Parameters:
                n1    -    refractive index of surrounding medium (complex)
                ns    -    refractive index of slab (complex)
                om    -    angular frequency (float)
                L     -    slab thickness in micrometers (float)
            
            Output:
                transfer function (complex) 
        
        """
        c = 299792458e6
        tas = 2*n1/(ns+n1)
        tsa = 2*ns/(ns+n1)
        
        return tas*tsa*exp(-1j*om*L/c*(ns-n1))
    
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
        dlg = FixedPointSelectionDialog(parent, reflist=refnames, sel = idp, isel = self.imethod, thickness = self.thickness, host = self.host, deviation = self.deviation, imaginary = self.imaginary)
        if dlg.ShowModal() == wx.ID_OK:
            idp, imethod, thickness, host, deviation, imaginary = dlg.GetValue()
            if idp>-1:
                self.imethod = imethod
                self.thickness = thickness
                self.host = host
                self.deviation = deviation
                self.imaginary = imaginary
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

class FixedPointSelectionDialog(wx.Dialog):
    def __init__(self, parent = None, title="Reference measurement", reflist = [], sel = 0, isel = 1, thickness = 1.0, host = 1.0, deviation = 2.0, imaginary = False):
        wx.Dialog.__init__(self, parent, title=title)
        self.label_reference = wx.StaticText(self, -1, "Reference scan")
        self.choice_reference = wx.Choice(self, -1, choices=reflist)
        self.label_interp = wx.StaticText(self, -1, "Interpolation method")
        self.choice_interp = wx.Choice(self, -1, choices=["Nearest neighbour", "Linear", "Quadratic spline", "Cubic spline"])
        self.label_thickness = wx.StaticText(self, -1, "Sample thickness (um)")
        self.input_thickness = wx.TextCtrl(self, -1, str(thickness))
        self.label_host = wx.StaticText(self, -1, "Host refractive index")
        self.input_host = wx.TextCtrl(self, -1, str(host))
        self.label_deviation = wx.StaticText(self, -1, "Deviation from linearity")
        self.input_deviation = wx.TextCtrl(self, -1, str(deviation))
        self.label_output = wx.StaticText(self, -1, "Computed value")
        self.choice_output = wx.Choice(self, -1, choices=["Real part","Imaginary part"])
        self.choice_output.SetSelection(imaginary*1.0)
        
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
        sizer.Add(self.label_thickness, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.input_thickness, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.label_host, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.input_host, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.label_deviation, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.input_deviation, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.label_output, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.choice_output, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(hbox, 0, wx.ALL|wx.EXPAND, 2)
        self.SetSizer(sizer)
        self.Fit()
        if sel>-1:
            self.choice_reference.SetSelection(sel)
        else:
            self.choice_reference.SetSelection(0)
        
        self.choice_interp.SetSelection(isel)
    
    def GetValue(self):
        return self.choice_reference.GetSelection(), self.choice_interp.GetSelection(), float(self.input_thickness.GetValue()), float(self.input_host.GetValue()), float(self.input_deviation.GetValue()), self.choice_output.GetSelection()==1
