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

    Post-processing filter functions
    
    Properties:
        modules    -    list of available filters
    
    Each filter must be implemented as a Filter class (see base.py).
    Filter classes contained in Python scripts within this folder will be
    automatically recognized and added to filter list. 

"""

import os
from terapy.filters.base import Filter
from terapy.core import check_py, filter_file
from terapy.core.parsexml import ParseAttributes
from terapy.core.dataman import DataArray
from terapy.core.axedit import AxisInfos
from wx.lib.pubsub import setupkwargs
from wx.lib.pubsub import pub
from xml.dom import minidom
import wx

####
def GetFilterFiles(dim=1):
    """
    
        Get saved filter banks for given dimension.
        
        Parameters:
            dim    -    dimension (int)
        
        Output:
            list of filter bank files (list of str)
    
    """
    # return a list of valid filter banks in filter_path
    from terapy.core import filter_path
    bank = FilterBank()
    inifiles = os.listdir(filter_path)
    ffiles = []
    for x in inifiles:
        fullpath = filter_path + os.path.normcase("/") + x
        try:
            res = bank.LoadFilterList(fullpath)
        except:
            res = None
        if res!=None:
            name = os.path.splitext(x)[0]
            fdim = -1
            xmldoc = minidom.parse(fullpath).getElementsByTagName('filters')
            for y in xmldoc:
                try:
                    name = y.attributes["name"].value
                    fdim = int(y.attributes["dimension"].value)
                except:
                    print "WARNING: missing name or dimension in filter file '" + fullpath + "'"
                break
            if fdim == dim:
                ffiles.append((fullpath,name))
    return ffiles

def GetModules(dim=1):
    """
    
        Get modules for a given dimension.
        
        Parameters:
            dim    -    dimension (int)
        
        Output:
            list of filters (list of Filter)
    
    """
    mods = []
    for x in modules:
        if x.dim==dim: mods.append(x)
    return mods

class FilterBank():
    """
    
        Filter bank class
    
    """
    def __init__(self, parent=None, children=[], filters=[], name = "Filter bank", dim = 1):
        """
        
            Initialization.
            
            Parameters:
                parent    -    parent window (wx.Window)
                children  -    child banks (list of FilterBank)
                filters   -    filters (list of Filter)
                name      -    filter bank name (str)
                dim       -    dimension of data treated by this bank (int)
        
        """
        self.filters = filters
        self.parent = parent
        self.name = name
        self.dim = dim
        self.children = children
        pub.subscribe(self.ComputeReference, "history.change_reference")
        pub.subscribe(self.RemoveReference, "history.clear_reference")
    
    def DefaultFilters(self):
        """
        
            Set default filters from default filter file.
        
        """
        # fill in default filter list
        self.filters = []
        # fill filter list with default filters
        if filter_file==None: return # no filter_file defined, can't proceed
        if os.path.exists(filter_file):
            self.LoadFilterList(fname=filter_file)

    def LoadFilterList(self, fname):
        """
        
            Load filter list from given file.
            
            Parameters:
                fname    -    file name (str)
            
            Output:
                list of filters (list of Filter)
        
        """
        # build available module list
        mods = GetModules(self.dim)
        ml = [x.__name__ for x in mods]
        # init tree
        self.filters = []
        # read file
        xmldoc = minidom.parse(fname).getElementsByTagName('filters')
        
        # parse filter list
        for x in xmldoc:
            try:
                name = x.attributes["name"].value
                fdim = int(x.attributes["dimension"].value)
            except:
                name = ""
                fdim = -1
                print "WARNING: missing name or dimension in filter file '" + fname + "'"
            
            if fdim == self.dim:
                self.name = name
                for y in x.childNodes:
                    if y.nodeName == 'item':
                        if ml.count(y.attributes['class'].value)>0:
                            n = ml.index(y.attributes['class'].value)
                            ft = mods[n]()
                            if y.attributes.has_key("name"):
                                ft.name = y.attributes["name"].value
                            else:
                                ft.name = ft.__extname__
                            self.filters.append(ft)
                            ParseAttributes(y.attributes,ft)
        if len(self.filters) == 0:
            print "WARNING: filter list empty. Either filter bank file is corrupt, or contains no compatible filter bank."
        return self.filters

    def SaveFilterList(self, fname):
        """
        
            Save current filter list to given file.
            
            Parameters:
                fname    -    file name (str)
        
        """
        doc = minidom.Document()
        croot = doc.createElement("config")
        croot.attributes["scope"] = "filters"
        doc.appendChild(croot)
        root = doc.createElement("filters")
        root.attributes["name"] = self.name
        root.attributes["dimension"] = self.dim
        croot.appendChild(root)
        for n in range(len(self.filters)):
            ft = self.filters[n]
            p = doc.createElement("item")
            root.appendChild(p)
            p.attributes["name"] = ft.name
            p.attributes["class"] = ft.__class__.__name__
            for x in ft.config:
                p.attributes[x] = str(getattr(ft,x))
                
        f = open(fname,'w')
        doc.writexml(f,indent="  ", addindent="  ", newl="\n")
        f.close()
    
    def InsertFilter(self, pos, ft):
        """
        
            Insert given filter at given position.
            
            Parameters:
                pos    -    position (int)
                ft     -    filter (Filter)
        
        """
        self.filters.insert(pos,ft)
        if ft.is_reference:
            self.RecomputeReference()
        pub.sendMessage("filter.change", inst=self)
    
    def AppendFilter(self, ft):
        """
        
            Append given filter at the end of the filter list.
            
            Parameters:
                ft    -    filter (Filter)
        
        """
        self.InsertFilter(len(self.filters), ft)
    
    def RemoveFilter(self, pos):
        """
        
            Remove filter in given position.
            
            Parameters:
                pos    -    position (int)
        
        """
        self.filters.pop(pos)
        pub.sendMessage("filter.change", inst=self)
    
    def __del__(self):
        """
        
            Actions necessary on filter bank deletion.
        
        """
        pub.unsubscribe(self.ComputeReference, "history.change_reference")
        pub.unsubscribe(self.RemoveReference, "history.clear_reference")
    
    def HasReference(self):
        """
        
            Tell if filter bank has reference filter.
            
            Output:
                True/False
        
        """
        for ft in self.filters:
            if ft.is_reference: return True
        return False
    
    def GetReferenceFilter(self):
        """
        
            Return reference filter, if any.
            
            Output:
                reference filter (Filter) or None
        
        """
        for ft in self.filters:
            if ft.is_reference: return ft
        return None
    
    def ComputeReference(self, inst):
        """
        
            Compute reference from given data if reference filter exists.
            
            Parameters:
                inst    -    array (DataArray)
                             or pubsub event data (DataArray)
        
        """
        if not(isinstance(inst,DataArray)):
            array = inst.data
        else:
            array = inst
        narray = DataArray(shape=array.shape[:])
        narray.coords = array.coords[:]
        narray.data = array.data[:]
        # build reference data
        # first apply previous filter banks
        bank = self
        while bank.parent!=None:
            bank = bank.parent
        while bank!=self:
            narray = bank.ApplyFilters(narray)
            bank = bank.children[-1]
        # then apply current filter bank up to reference filter
        for ft in self.filters:
            if not(ft.is_reference):
                if ft.is_active:
                    ft.apply_filter(narray)
            else:
                ft.ref = narray
                ft.source = array
                if inst!=array:
                    pub.sendMessage("filter.change", inst=self) # send filter change notification with filter bank as object
                break
    
    def RecomputeReference(self):
        """
        
            Recompute reference data for reference filter, if any.
        
        """
        for ft in self.filters:
            if ft.is_reference and ft.is_active:
                self.ComputeReference(ft.source)
                break
    
    def RemoveReference(self, inst=None):
        """
        
            Remove reference filter.
            
            Parameters:
                inst    -    pubsub event data
        
        """
        # search for reference filter, remove if exist
        if self in inst:
            for n in range(len(self.filters)):
                if self.filters[n].is_reference:
                    ft = self.filters.pop(n)
                    # recompute reference in children if one exists
                    for x in self.children:
                        x.RecomputeReference()
                    pub.sendMessage("filter.change", inst=self)
                    return ft
            return None 

    def ApplyFilters(self, array):
        """
        
            Apply filter bank to given data array.
            
            Parameters:
                array    -    data array (DataArray)
        
        """
        # apply all filters
        narray = array.Copy()
        units = [x.units for x in narray.axes]
        units.append(narray.input.units)

        for ft in self.filters:
            if ft.is_active:
                ft.apply_filter(narray)
                units = ft.get_units(units)
        
        for n in range(len(narray.axes)): narray.axes[n].units = units[n]
        narray.input.units = units[-1]
        return narray
    
    def GetUnits(self, units):
        """
        
            Return how given physical units are modified by filter bank
            
            Parameters:
                units    -    list of dim+1 units
            
            Output:
                units of coordinates and data after processing (list of quantities) 
        
        """
        # compute units after processing
        for ft in self.filters:
            if ft.is_active:
                units = ft.get_units(units)
        
        for x in units: x._magnitude = 1.0
        return units
        

# import filter classes
curdir = os.path.dirname(__file__)
from terapy.core import parse_modules
modules = parse_modules(__package__, curdir, Filter)

# search for custom modules
from terapy.core import module_path
if os.path.exists(module_path):
    modules.extend(parse_modules("custom.filter.", module_path, Filter))
