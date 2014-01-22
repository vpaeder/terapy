#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2013-2014  Vincent Paeder
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

    Generic scan event class.

"""
    
import wx
from terapy.core import icon_path
from wx.lib.pubsub import Publisher as pub

class ScanEvent():
    """
    
        Generic scan event class.
        
        Properties:
            __extname__    -    long name (str)
    
    """
    __extname__ = "Generic event"
    def __init__(self, parent = None):
        """
        
            Initialization.
            
            Parameters:
                parent    -    parent window (wx.Window)
        
        """
        self.is_loop = False
        self.is_display = False
        self.is_save = False
        self.is_axis = False
        self.is_input = False
        self.is_root = False
        self.is_active = True
        self.is_visible = True
        self.can_run = True
        self.host = parent
        self.name = self.__extname__
        self.itmList = []
        self.propNodes = []
        self.propNames = []
        self.m_id = 0
        #self.propFont = wx.Font(8,wx.DECORATIVE,wx.NORMAL,wx.NORMAL)
        #self.propColour = "#3F3F3F"
        self.config = [] # variables to be saved in config files
        pub.subscribe(self.stop, "scan.stop")
    
    def __del__(self):
        """
        
            Actions necessary on scan event deletion.
        
        """
        pub.unsubscribe(self.stop, "scan.stop")
    
    def run(self, data):
        """
        
            Run scan event.
            
            Parameters:
                data    -    measurement (Measurement)
        
        """
        return True

    def stop(self, inst=None):
        """
        
            Stop scan.
            
            Parameters:
                inst    -    pubsub event data
        
        """
        self.can_run = False
    
    def refresh(self):
        """
        
            Refresh scan event.
        
        """
        self.can_run = True
        
    def get_operation_count(self):
        """
        
            Tell how many "operations" this event will generate.
            Normal events do one operation. Loops do one operation per iteration.
            
            Output:
                number of operations (int)
        
        """
        return 1
    
    def run_children(self, data):
        """
        
            Run scan event children.
            
            Parameters:
                data    -    measurement (Measurement)
        
        """
        for x in self.itmList:
            if self.can_run:
                ev = self.host.GetItemData(x).GetData()
                if ev.is_active:
                    if ev.is_display or ev.is_save:
                        ev.run(data)
                    elif ev.is_input:
                        ev.run(data)
                        data.current += 1
                    elif ev.is_axis:
                        ev.run([])
                    elif ev.is_loop:
                        data.IncrementScanDimension(self.m_ids)
                        ev.run(data)
        return True
    
    def set(self, parent=None):
        """
        
            Run scan event configuration procedure.
            
            Parameters:
                parent    -    parent window (wx.Window)
            
            Output:
                True if successful
        
        """
        return True
    
    def get_children(self):
        """
        
            Get scan event children. Wrapper to TreeCtrl function.
            
            Output:
                children as list of ScanEvent
        
        """
        itm = self.host.FindItem(self)
        return self.host.GetItemChildren(itm,ScanEvent)
        
    def populate(self):
        """
        
            Populate host tree structure with properties.
        
        """
        if len(self.propNodes)>0:
            self.create_property_root()
            self.set_property_nodes(expand=True)
    
    def create_property_root(self):
        """
        
            Create property root in host tree structure.
        
        """
        itm = self.host.FindItem(self)
        if self.get_property_node()==None:
            propRoot = self.host.AppendItem(itm,"Properties")
            self.host.SetItemPyData(propRoot,PropertyNode())
        else:
            self.host.DeleteChildren(self.get_property_node())
    
    def get_property_node(self, n=-1):
        """
        
            Return item corresponding to given property node index
             
            Parameters:
                n    -    property node index (if n==-1, return property root)
            
            Output:
                tree item (wx.TreeItem)
        
        """
        root = self.host.FindItem(self)
        propRoot = self.host.GetItemChildren(root,PropertyNode)
        if n==-1: # return root
            if len(propRoot)==0:
                return None
            else:
                return propRoot[0]
        else: # return property node number n
            itms = self.host.GetItemChildren(propRoot[0])
            return itms[n]
            
    
    def set_property_nodes(self, expand=False):
        """
        
            Set property node values.
            
            Parameters:
                expand    -    if True, expand property folder, collapse if False
        
        """
        root = self.get_property_node()
        if root!=None:
            children = self.host.GetItemChildren(root)
            if len(children) != len(self.propNames):
                self.host.DeleteChildren(root)
                for n in range(len(self.propNames)):
                    self.host.AppendItem(root,self.propNames[n]+": "+str(self.propNodes[n]))
                children = self.host.GetItemChildren(root)
            else:
                for n in range(len(children)):
                    self.host.SetItemText(children[n],self.propNames[n]+": "+str(self.propNodes[n]))
            
            children.append(root)
            propFont = wx.Font(8,wx.DECORATIVE,wx.NORMAL,wx.NORMAL)
            propColour = "#3F3F3F"
            for x in children:
                self.host.SetItemFont(x,propFont)
                self.host.SetItemTextColour(x,propColour)
            if expand:
                self.host.Expand(root)
        
    def set_property(self, pos, val):
        """
        
            Set given property to given value.
            
            Parameters:
                pos    -    property index (int)
                val    -    value
        
        """
        self.propNodes[pos] = val
    
    def edit_label(self, event, pos):
        """
        
            Actions triggered by edit tree label event corresponding to given property node.
            
            Parameters:
                event    -    wx.Event
                pos      -    property index (int)
        
        """
        pass
    
    def check_validity(self, data):
        """
        
            Check whether given data can be processed by this event.
             
            Parameters:
                data    -    data array (DataArray) or measurement (Measurement)
            
            Output:
                True if yes
        
        """
        return True
    
    def get_icon(self):
        """
        
            Return scan event icon.
            
            Output:
                16x16 icon (wx.Bitmap)
        
        """
        return wx.Image(icon_path + "empty.png").ConvertToBitmap()
    

class PropertyNode():
    """
    
        Property node class
        
        Differentiate property nodes from other tree items.
    
    """
    def __init__(self):
        """
        
            Initialization.
        
        """
        self.is_loop = False
        self.is_root = False
