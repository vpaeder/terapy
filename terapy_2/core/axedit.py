#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2014  Vincent Paeder
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

    Classes for axes labels and units management

"""

import wx.grid
from wx.lib import sheet
from terapy.core import default_units
from pint import UnitRegistry
from numpy import log10

urg = UnitRegistry()
Q_ = urg.Quantity
for y in [['hertz','Hz'],['meter','m'],['second','s'],['volt','V'],['ampere','A']]:
    for x in [['atto',1.0e-18,'a'],['femto',1.0e-15,'f'],['pico',1.0e-12,'p'],['nano',1.0e-9,'n'],['micro',1.0e-6,'u'],['milli',1.0e-3,'m'],['kilo',1.0e3,'k'],['mega',1.0e6,'M'],['giga',1.0e9,'G'],['tera',1.0e12,'T'],['peta',1.0e15,'P'],['exa',1.0e18,'E']]:
        urg.define('%s%s = %1.0e*%s = %s%s' % (x[0],y[0],x[1],y[0],x[2],y[1]))

# default units
du = {}
for x in default_units:
    try:
        du[x] = Q_(1.0,urg[default_units[x]])
    except:
        print "WARNING: can't understand units'%s' " % (x)

class AxesPropertiesDialog(wx.Dialog):
    """
    
        Axes properties selection dialog
    
    """
    def __init__(self, parent = None, title="Axes properties", axlist=[], read_only = [False,False], format = True):
        """
        
            Initialization.
            
            Parameters:
                parent    -    parent window (wx.Window)
                title     -    dialog title (str)
                axlist    -    list of axes properties (list of AxisInfos)
        
        """
        wx.Dialog.__init__(self, parent, title=title, size=(400,-1))
        self.sheet = sheet.CSheet(self)
        self.button_OK = wx.Button(self, wx.ID_OK)
        self.button_Cancel = wx.Button(self, wx.ID_CANCEL)
        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.AddStretchSpacer(1)
        hbox.Add(self.button_Cancel, 0, wx.RIGHT|wx.ALIGN_RIGHT, 5)
        hbox.Add(self.button_OK, 0, wx.RIGHT|wx.ALIGN_RIGHT, 5)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.sheet, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(hbox, 0, wx.ALL|wx.EXPAND, 2)
        self.SetSizerAndFit(sizer)
        
        # construct list of physical units
        self.format = format
        units = {}
        for x in urg._units:
            sym = urg._units[x].symbol
            if not(units.has_key(sym)):
                try:
                    units[sym] = urg[sym]
                except:
                    pass
        
        # add units of axlist items if not in list
        ulist = [x.units for x in units.values()]
        for x in axlist:
            if ulist.count(x.units.units)==0:
                units["%s" % (x.units.units)] = x.units
                ulist.append(x.units.units)
        
        # sort list of units
        from collections import OrderedDict
        units = OrderedDict(sorted(units.items(), key=lambda t: t[0].lower()))
        
        # reformat names
        self.units = OrderedDict()
        while len(units)>0:
            p = units.popitem(0)
            self.units["%s (%s)" % (p[1].units,p[0])] = p[1]
        
        # fill sheet
        self.sheet.SetSelectionMode(0)
        self.table = AxesList([x.copy() for x in axlist],self.units)
        self.sheet.SetTable(self.table)
        self.sheet.SetMaxSize((-1,200))
        self.sheet.SetMinSize((-1,200))
        self.sheet.AutoSizeColumn(1)
        
        # assign combo editor to 2nd column
        self.editor = wx.grid.GridCellChoiceEditor(self.units.keys(),allowOthers=True)
        for n in range(len(axlist)):
            self.sheet.SetCellEditor(n,1,self.editor)
            self.sheet.SetReadOnly(n,0,read_only[0])
            self.sheet.SetReadOnly(n,1,read_only[1])
        
        self.Fit()
    
    def GetValue(self):
        """
        
            Return dialog values.
            
            Output:
                list of AxisInfos objects
        
        """
        if self.format:
            for x in self.table.data:
                x.units = FormatUnits(x.units)
        return self.table.data
    
    def Destroy(self, event=None):
        """
        
            Events preceding dialog destruction.
            
            Parameters:
                event    -    wx.Event
        
        """
        self.sheet.SaveEditControlValue()
        self.sheet.HideCellEditControl()
        wx.Dialog.Destroy(self)

class AxesList(wx.grid.PyGridTableBase):
    """
    
        Table base class for point list
    
    """
    def __init__(self, data=[], units=[]):
        
        """
        
            Initialization.
            
            Parameters:
                data     -    list of AxisInfos  
        
        """
        wx.grid.PyGridTableBase.__init__(self)
        self._cols = ["Label","Units"]
        self.data = data
        self.units = units
    
    def GetColLabelValue(self, col):
        """
        
            Return column label for given index.
            
            Parameters:
                col    -    column index (int)
            
            Output:
                column label (str)
        
        """
        return self._cols[col]

    def GetNumberRows(self):
        """
        
            Return number of rows.
            
            Output:
                number of rows (int)
        
        """
        return len(self.data)

    def GetNumberCols(self):
        """
        
            Return number of columns.
            
            Output:
                number of columns (int)
        
        """
        return len(self._cols)
    
    def FormatValue(self, units):
        """
        
            Return formatted units name + symbol.
            
            Parameters:
                units    -    pint units (pint.Quantity)
            
            Output:
                units name + symbol (str)
        
        """
        return "%s (%s)" % ("{:P}".format(units),"".join("{:~}".format(units).split(' ')[1:]))
    
    def GetValue(self, row, col):
        """
        
            Return value for given row and column index.
            
            Parameters:
                row    -    row index (int)
                col    -    column index (int)
            
            Output:
                value (float)
        
        """
        if col==0:
            return self.data[row].name
        elif col==1:
            try:
                return self.FormatValue(self.data[row].units)
            except:
                pass
    
    def SetValue(self, row, col, val):
        """
        
            Set value of given row and column index.
            
            Parameters:
                row    -    row index (int)
                col    -    column index (int)
                value  -    value (float)
        
        """
        if col==0:
            self.data[row].name = val
        elif col==1:
            try:
                self.data[row].units = self.units[val]
            except:
                try:
                    self.data[row].units = urg[str(val)]
                except:
                    pass

class AxisInfos():
    """
        
        Axis infos class - report on axis name and units
        
    """
    def __init__(self, name, units):
        """
        
            Initialization.
            
            Parameters:
                name    -    axis name (str)
                units   -    axis units (str or quantities)
        
        """
        self.name = name
        if isinstance(units,str):
            # units given as string => try to match with physical units
            try:
                # try to create units by parsing text
                self.units = 1.0 * urg[units]
            except:
                # if this failed, store units as text
                self.units = units
        else:
            self.units = units
    
    def __str__(self):
        """
        
            Return axis name.
            
            Output:
                axis name (str)
        
        """
        return self.label()
    
    def __repr__(self):
        return "<AxisInfos(%s, %s) instance at %s>" % (self.name, self.pretty_units(), hex(id(self)))
    
    def name(self):
        """
        
            Return axis name.
            
            Output:
                name (str)
        
        """
        return self.name
    
    def pretty_units(self):
        """
        
            Return formatted units.
            
            Output:
                units (str)
        
        """
        try:
            # format each quantity as x^n
            from collections import OrderedDict
            nunits = OrderedDict(sorted(self.units.units.items(), key=lambda t: t[1], reverse=True))
            t = ""
            for x in nunits.keys():
                if len(t)>0:
                    t = "%s $\\cdot$" % (t)
                if nunits[x]==1:
                    t = "%s %s" % (t, urg._units[x].symbol)
                else:
                    t = "%s %s$^{%d}$" % (t, urg._units[x].symbol,nunits[x])
            if self.units.magnitude!=1:
                # format scale factor: if <0.1 or >=100, use v x 10^n notation, otherwise use plain number
                if self.units.magnitude<0.1 or self.units.magnitude>=100:
                    e0 = int(log10(self.units.magnitude))
                    v0 = self.units.magnitude/(10.0**e0)
                    return "%s $\\times %0.1f \\cdot 10^{%d}$" % (t, v0, e0)
                else:
                    if self.units.magnitude == int(self.units.magnitude):
                        return "%s $\\times %d$" % (t, self.units.magnitude)
                    else:
                        return "%s $\\times %0.1f$" % (t, self.units.magnitude)
            else:
                return t
        except:
            # unhandled case => return units as is
            return " %s" % (self.units)
    
    def label(self):
        """
        
            Return axis label (name + units).
            
            Output:
                name + units (str)
        
        """
        return "%s (%s )" % (self.name, self.pretty_units())
    
    def copy(self):
        """
        
            Create copy of current object.
        
            Return:
                copy of object (AxisInfos)
        
        """
        
        return AxisInfos(self.name,urg["%s" % (self.units)])

def FormatUnits(units):
    """
    
        Format given units in default units.
        Parameters:
            units    -    pint units (pint.Quantity)
        Output:
            processed units (pint.Quantity)
    
    """
    # convert units to default units
    keys = units.units.keys()
    for x in keys:
        for y in du.values():
            ux = urg[x].dimensionality
            ux_inv = (1.0/urg[x]).dimensionality
            uy = y.dimensionality
            cur = units.units[x]
            
            if uy==ux and cur>0:
                # same dimensionality as one default unit
                units = units/urg[x]*urg[x].to(y)
                break
            elif uy==ux and cur<0:
                # same dimensionality as one default unit
                # but 1/unit => must check that no other default
                # unit with dimensionality 1/... can be found
                if [u.dimensionality for u in du.values()].count(ux_inv)==0:
                    units = units*urg[x]/urg[x].to(y)
                    break
            elif uy==ux_inv and cur<0:
                units = units*urg[x]*(1.0/urg[x]).to(y)
                break
    
    # simplify units
    for x in du.values():
        # see if one default unit has the inverse dimensionality of another one
        ux = x.dimensionality
        ux_inv = (1.0/x).dimensionality
        if [u.dimensionality for u in du.values()].count((1/x).dimensionality):
            # if yes, check that the units don't contain both
            idx = [u.dimensionality for u in du.values()].index((1/x).dimensionality)
            x_inv = du.values()[idx]
            c_x = units.units.keys().count(x.units.keys()[0])
            c_x_inv = units.units.keys().count(x_inv.units.keys()[0])
            if c_x>0 and c_x_inv>0:
                # if they do, divide units by minimum common power 
                i_x = units.units.keys().index(x.units.keys()[0]) 
                i_x_inv = units.units.keys().index(x_inv.units.keys()[0])
                v_x = units.units.values()[i_x]
                v_x_inv = units.units.values()[i_x_inv]
                dv = min([v_x,v_x_inv])
                units = units/(x**dv)/(x_inv**dv)
    
    return units

def ConvertUnits(old, new, ask_incompatible=True):
    """
    
        Convert from between two sets of units and check compatibility. Return scale factors if units are compatible.
        Parameters:
            old    -    old set of units (list of AxisInfos)
            new    -    new set of units (list of AxisInfos)
        Output:
            scale factors between sets of units (list of float)
    
    """
    factors = [1.0]*len(new)
    for n in range(len(new)):
        try:
            factors[n] = float(old[n].units.magnitude)/float(new[n].units.magnitude)
            factors[n] *= float(old[n].units.to(new[n].units).magnitude)/float(old[n].units.magnitude)
            old[n] = new[n]
        except:
            if ask_incompatible:
                if wx.MessageBox("New units for axis %d (%s) are incompatible with old ones (%s). Apply anyway?" % (n, "{:P}".format(new[n].units.units), "{:P}".format(old[n].units.units)), "Incompatible units", style=wx.YES | wx.NO) == wx.YES:
                    old[n] = new[n]
            else:
                try:
                    old[n] = new[n]
                except:
                    old.append(new[n])
        old[n].units = FormatUnits(old[n].units)
    
    return factors
