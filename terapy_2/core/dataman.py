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

    Container classes for measurement data.

"""

from treectrl import SubTree
import numpy as np
from terapy.core.axedit import AxisInfos, ConvertUnits

class Measurement():
    """
    
    Measurement container class
    Store several data arrays corresponding each to one measured quantity
    during a measurement sequence.
    
    """
    def __init__(self, name="", events=None):
        """
        
            Initialization
            
            Parameters:
                name    -    name of measurement (str)
                events  -    measurement events (ScanEvent)
        
        """
        self.name = name
        self.events = events # measurement events
        self.count = 0 # number of data arrays
        self.total = 0 # total number of steps
        self.current = 0 # current step
        self.xml = "" # store event tree
    
    def BuildDataTree(self):
        """
        
            Build data arrays from given measurement events
        
        """
        # allocate data arrays
        self.GetShapes()
        self.data = map(lambda x: DataArray(x,self.name),self.shape)
        for n in range(self.count):
            self.data[n].input = self.inputs[n]
            self.data[n].axes = self.axes[n]
            self.total += np.prod(self.opcount[n])
    
    def GetShapes(self, events=None, shape = [], opcount = [], axes = []):
        """
        
            Compute shapes of data arrays from given measurement events
            Result stored as self.shape
            
            Parameters:
                events    -    measurement events (SubTree). If None, takes self.events
                shape     -    shapes of previously processed arrays, used internally
                opcount   -    number of operations for previously processed arrays, used internally
                axes      -    axis devices of previously processed dimensions, used internally
            
            Results:
                self.shape    -    shape of data arrays for given measurement events
                self.opcount  -    number of operations for data arrays for given measurement events
            
        """
        # construct shapes of recipient arrays and fetch axes names
        if events==None:
            events = self.events
            Nt = events.CountOccurrences('is_input',True)
            events.data.m_ids = range(Nt)
            shape = []
            opcount = []
            axes = []
            self.shape = [[]]*Nt
            self.opcount = [[]]*Nt
            self.inputs = [[]]*Nt
            self.axes = [[]]*Nt
        Nt = events.CountOccurrences('is_input',True) # number of data arrays to build (1 per measured qty)
        if Nt>0:
            for x in events.items:
                x.data.m_id = self.count # set reference to measurement array
                opcount.append(x.data.get_operation_count())
                if x.data.is_input:
                    # store input name and axis names
                    self.shape[self.count] = shape[:]
                    self.opcount[self.count] = opcount[:]
                    self.axes[self.count] = axes[:]
                    self.inputs[self.count] = AxisInfos(x.data.inlist[x.data.input].qtynames[x.data.index], x.data.inlist[x.data.input].units[x.data.index])
                    self.count+=1
                if x.data.is_display or x.data.is_save:
                    x.data.m_id = self.count-1 # assume that the plot function is after an input => will plot 1st qty present before itself 
                if isinstance(x,SubTree):
                    cshape = shape[:]
                    copcount = opcount[:]
                    caxis = axes[:]
                    if hasattr(x.data,'N'):
                        # this event is a loop with some dimension
                        cshape.append(x.data.N)
                        # if the loop acts on an axis, save axis reference
                        if hasattr(x.data,'axlist'):
                            caxis.append(AxisInfos(x.data.axlist[x.data.axis].qtynames,x.data.axlist[x.data.axis].units))
                        else:
                            caxis.append(None)
                    self.GetShapes(x,cshape,copcount,caxis)
                    # must store which data array indices are in this loop
                    x.data.m_ids = range(x.data.m_id,self.count)
    
    def SetCurrentValue(self, narray, value, inc=False, dec=False):
        """
        
            Set value for current position of selected data array
            
            Parameters:
                narray   -    array index (int)
                value    -    value (float)
                inc      -    increment index after (bool)
                dec      -    decrement index after (bool)
            
        """
        if narray<self.count:
            arr = self.data[narray]
            if len(arr.idx)>0:
                arr.data[tuple(arr.idx)] = value
                if inc:
                    arr.Increment()
                elif dec:
                    arr.Decrement()
            else:
                arr.data = value
    
    def GetCurrentValue(self, narray):
        """
        
            Get value at current position in selected data array
            
            Parameters:
                narray    -    array index (int)
            
            Output:
                value (float)
        
        """
        if narray<self.count:
            arr = self.data[narray]
            if len(arr.idx)>0:
                return arr.data[tuple(arr.idx)]
            else:
                return arr.data
    
    def SetCoordinateValue(self, narrays, value):
        """
        
            Set value for current coordinate axis of selected data arrays
            
            Parameters:
                narrays   -    list of array indices (list of int)
                value    -    value (float)
            
        """
        for narray in narrays:
            if narray<self.count:
                arr = self.data[narray]
                arr.coords[arr.scanDim][arr.idx[arr.scanDim]] = value
    
    def GetCoordinateValue(self, narrays):
        """
        
            Get value for current coordinate axis of selected data arrays
            
            Parameters:
                narrays   -    list of array indices (list of int)
            
            Output:
                list of values (list of float)
        
        """
        vals = []
        for narray in narrays:
            if narray<self.count:
                arr = self.data[narray]
                vals.append(arr.coords[arr.scanDim][arr.idx[arr.scanDim]])
        
        return vals
    
    def IncrementScanDimension(self, narrays):
        """
        
            Increment scan dimension of selected data arrays
            
            Parameters:
                narrays   -    list of array indices (list of int)
        
        """
        for narray in narrays:
            if narray<self.count:
                arr = self.data[narray]
                arr.scanDim += 1
                if arr.scanDim >= len(arr.shape):
                    arr.scanDim = len(arr.shape)-1
    
    def DecrementScanDimension(self, narrays):
        """
        
            Decrement scan dimension of selected data arrays
            
            Parameters:
                narrays   -    list of array indices (list of int)
        
        """
        for narray in narrays:
            if narray<self.count:
                arr = self.data[narray]
                arr.scanDim -= 1
                if arr.scanDim < 0:
                    arr.scanDim = 0
    
    def SetScanDimension(self, narrays, dim):
        """
        
            Set scan dimension of selected data arrays
            
            Parameters:
                narrays   -    list of array indices (list of int)
                dim       -    dimension (int)
        
        """
        for narray in narrays:
            if narray<self.count:
                arr = self.data[narray]
                arr.scanDim = dim
    
    def GetScanDimension(self, narrays):
        """
        
            Get scan dimension of selected data arrays
            
            Parameters:
                narrays   -    list of array indices (list of int)
            
            Output:
                list of dimensions (list of int)
        
        """
        vals = []
        for narray in narrays:
            if narray<self.count:
                arr = self.data[narray]
                vals.append(arr.scanDim)
        
        return vals
    
    def SetScanPosition(self, narrays, pos):
        """
        
            Set scan position for current scan dimension of selected data array
            
            Parameters:
                narray   -    array index (int)
                pos      -    position (int)
        
        """
        for narray in narrays:
            if narray<self.count:
                arr = self.data[narray]
                arr.idx[arr.scanDim] = pos
    
    def Increment(self, narrays):
        """
        
            Increment scan position for current scan dimension of selected data array
            
            Parameters:
                narray   -    array index (int)
        
        """
        for narray in narrays:
            if narray<self.count:
                arr = self.data[narray]
                arr.Increment(arr.scanDim)
    
    def Decrement(self, narrays):
        """
        
            Decrement scan position for current scan dimension of selected data array
            
            Parameters:
                narray   -    array index (int)
        
        """
        for narray in narrays:
            if narray<self.count:
                arr = self.data[narray]
                arr.Decrement(arr.scanDim)
    
    def ResetCounter(self,narrays):
        """
        
            Reset scan position in selected arrays
            
            Parameters:
                narrays   -    array indices (list of int)
        
        """
        self.current = 0
        for narray in narrays: 
            if narray<self.count:
                arr = self.data[narray]
                idx = arr.idx
                arr.idx = idx*0

class DataArray():
    """
    
        Data array container class
        Store data in an array of specified shape, with corresponding coordinate axes
    
    """
    def __init__(self, shape=[], name = 'Current scan'):
        """
        
            Initialization
            
            Parameters:
                shape    -    array shape (list)
                name     -    array name
        
        """
        self.shape = shape # shape of data array
        self.coords = [] # coordinates along each axis
        self.data = np.zeros(shape)*np.nan # data
        self.idx = np.array(map(int,np.zeros(len(shape)))) # current index
        self.plot = None # where the data is plotted
        self.color = None # plot color
        self.name = name
        self.scanDim = 0 # which dimension is currently scanned
        self.filename = "" # file name
        self.input = None # input device
        self.axes = [None]*len(shape) # axis devices
        map(lambda x: self.coords.append(np.zeros(x)),shape)
    
    def Increment(self,dim):
        """
        
            Increment position along selected scan dimension
            
            Parameters:
                dim    -    array dimension (int)
        
        """
        if dim<0 or dim>=len(self.idx): return # wrong dimension index
        # increment dimension 'dim' by one
        self.idx[dim] += 1
        for n in range(dim,0,-1):
            if self.idx[n] >= self.shape[n]:
                self.idx[n] = 0
                self.idx[n-1] += 1
        if self.idx[0] >= self.shape[0]:
            self.idx[0] = 0
    
    def Decrement(self,dim):
        """
        
            Decrement position along selected scan dimension
            
            Parameters:
                dim    -    array dimension (int)
        
        """
        if dim<0 or dim>=len(self.idx): return # wrong dimension index
        # decrement dimension 'dim' by one
        self.idx[dim] -= 1
        for n in range(dim,0,-1):
            if self.idx[n] < 0:
                self.idx[n] = self.shape[n]-1
                self.idx[n-1] -= 1
        if self.idx[0] < 0:
            self.idx[0] = self.shape[0]-1
    
    def SetPosition(self,dim,pos):
        """
        
            Set position counter along selected scan dimension
            
            Parameters:
                dim    -    array dimension (int)
                pos    -    position index (int)
        
        """
        if dim<0 or dim>=len(self.idx): return # wrong dimension index
        if pos>=0 and pos<self.shape[dim]:
            self.idx[dim] = pos
    
    def GetPosition(self,dim):
        """
        
            Get position counter along selected scan dimension
            
            Parameters:
                dim    -    array dimension (int)
            
            Output:
                position index (int)
        
        """
        if dim<0 or dim>=len(self.idx): return # wrong dimension index
        return self.idx[dim]
    
    def SetValue(self, value):
        """
        
            Set array value at current scan position
            
            Parameters:
                value    -    value (float)
        
        """
        # set value of current index
        self.data[tuple(self.idx)] = value
    
    def GetValue(self):
        """
        
            Get array value at current scan position
            
            Output:
                value (float)
        
        """
        # get value of current index
        return self.data[tuple(self.idx)]
    
    def SetCoordinateValue(self, value):
        """
        
            Set value for current coordinate axis
            
            Parameters:
                value    -    value (float)
            
        """
        self.coords[self.scanDim][self.idx[self.scanDim]] = value
    
    def GetCoordinateValue(self):
        """
        
            Get value for current coordinate axis
            
            Output:
                coordinate value (float)
        
        """
        return self.coords[self.scanDim][self.idx[self.scanDim]]
    
    def Copy(self):
        """
        
            Create a copy of itself.
            
            Output:
                copy of itself (DataArray)
        
        """
        narray = DataArray(shape=self.shape[:])
        narray.coords = self.coords[:]
        narray.data = self.data[:]
        narray.idx = self.idx[:]
        narray.plot = self.plot
        narray.color = self.color
        narray.name = self.name
        narray.scanDim = self.scanDim
        narray.filename = self.filename
        narray.input = self.input.copy()
        narray.axes = [x.copy() for x in self.axes]
        
        return narray

    def Rescale(self, new_labels, defaults = []):
        """
        
            Rescale data according to given axes settings.
            
            Parameters:
                new_labels    -    list of new labels+units (list of AxisInfos)
                defaults      -    default values if none are currently set (list of AxisInfos)
        
        """
        # build list to convert
        old_labels = self.axes[:]
        old_labels.append(self.input)
        for n in range(len(old_labels)):
            if old_labels[n]==None:
                # label not defined
                if len(defaults)>n:
                    # take default if it exists
                    old_labels[n] = defaults[n]
                elif len(new_labels)>n:
                    # otherwise, take new value if it exists 
                    old_labels[n] = new_labels[n]
        
        # check that new labels are defined
        for n in range(len(new_labels)):
            if new_labels[n]==None:
                # label not defined, set as old label
                new_labels[n] = old_labels[n]
        
        factors = ConvertUnits(old_labels, new_labels, ask_incompatible = False)
        for n in range(len(factors)):
            if n<len(self.shape):
                self.axes[n] = old_labels[n]
            else:
                self.input = old_labels[n]
            if factors[n]!=1:
                if n<len(self.shape):
                    self.coords[n] *= factors[n]
                else:
                    self.data *= factors[n]
