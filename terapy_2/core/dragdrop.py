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

    Drag and drop classes

"""

import wx

class GenericDrop(wx.PyDropTarget):
    """
    
        All-purpose drop target
    
    """
    def __init__(self, func):
        wx.PyDropTarget.__init__(self)
        self.func = func
    
    def OnData(self, x, y, d):
        if self.GetData():
            ldata = self.data.GetData()
            self.func(x,y,ldata)
            pass

class EventDrop(GenericDrop):
    """
    
        ScanEvent drop target
    
    """
    def __init__(self, func):
        GenericDrop.__init__(self, func)
        self.func = func
        self.data = EventDragObject()
        self.SetDataObject(self.data)
        
class HistoryDrop(GenericDrop):
    """
    
        History item drop target
    
    """
    def __init__(self, func):
        GenericDrop.__init__(self, func)
        self.func = func
        self.data = HistoryDragObject()
        self.SetDataObject(self.data)

class FilterDrop(GenericDrop):
    """
    
        Filter item drop target
    
    """
    def __init__(self, func):
        GenericDrop.__init__(self, func)
        self.func = func
        self.data = FilterDragObject()
        self.SetDataObject(self.data)

class GenericDragObject(wx.PyDataObjectSimple): 
    """
    
        All-purpose drag object
    
    """
    def __init__(self, fmt='None'): 
        wx.PyDataObjectSimple.__init__(self, wx.CustomDataFormat(fmt)) 
        self.data = None

    def GetDataSize(self): 
        return 1
        
    def GetDataHere(self):
        if self.data!=None: 
            return "data"
        else:
            return None
    
    def GetData(self):
        return self.data
    
    def SetData(self, data):
        self.data = data
        return True
 
class EventDragObject(GenericDragObject): 
    """
    
        ScanEvent drag object
    
    """
    def __init__(self): 
        GenericDragObject.__init__(self,'SubTree') 

class HistoryDragObject(GenericDragObject): 
    """
    
        History item drag object
    
    """
    def __init__(self): 
        GenericDragObject.__init__(self,'HistoryItem') 

class FilterDragObject(GenericDragObject): 
    """
    
        Filter item drag object
    
    """
    def __init__(self): 
        GenericDragObject.__init__(self,'FilterItem') 
