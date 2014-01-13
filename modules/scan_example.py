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

from terapy.scan.base import ScanEvent

class ScanExample(ScanEvent):
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
                parent    -    parent control (wx.TreeCtrl)
        """
        ScanEvent.__init__(self, parent)
        self.is_loop = False # set to True if this event implements a loop of some sort
        self.is_display = False # set to True if this event is meant to display something (i.e. plot/print/...)
        self.is_save = False # set to True if this event saves data to somewhere
        self.is_axis = False # set to True if this event acts on axis devices
        self.is_input = False # set to True if this event acts on input devices
        self.is_active = True # set to True if this event is active by default
        self.is_visible = True # set to True if this event is visible in the interface
        self.can_run = True # tell if the event can run (set to True on reset)
        self.host = parent # parent control (wx.TreeCtrl)
        self.name = self.__extname__ # event display name (str)
        self.propNames = [] # property names, as displayed in the interface
        self.propNodes = [] # property values
        self.config = [] # variables to be saved in config files
    
    def run(self, meas):
        """
            Run scan event.
            Parameters:
                meas    -    measurement (Measurement)
        """
        # Insert here what the event should do with the measurement data structure.
        # See Measurement class for details.
        return ScanEvent.run(self, meas)
    
    def stop(self, inst=None):
        """
            Stop scan.
            Parameters:
                inst    -    pubsub event data
        """
        # Insert here what should be done when the measurement stops
        ScanEvent.stop(self, inst)
    
    def refresh(self):
        """
            Refresh scan event.
        """
        # Insert here what should be done to refresh the state of the scan event.
        ScanEvent.refresh(self)
        
    def run_children(self, meas):
        """
            Run scan event children.
            Parameters:
                meas    -    measurement (Measurement)
        """
        # Insert here how children should be called from within this scan event
        return ScanEvent.run_children(self, meas)
    
    def set(self, parent=None):
        """
            Run scan event configuration procedure.
            Parameters:
                parent    -    parent window (wx.Window)
            Output:
                True if successful
        """
        # Insert here configuration actions (e.g. pop dialog box)
        return ScanEvent.set(self, parent)
    
    def edit_label(self, event, pos):
        """
            Actions triggered by edit tree label event corresponding to given property node.
            Parameters:
                event    -    wx.Event
                pos      -    property index (int)
        """
        # Insert here what should be done to display adequate editor when properties are edited in place
        # (i.e. inside the host TreeCtrl). See Read event for an example of custom editor.
        ScanEvent.edit_label(self, event, pos)
    
    def check_validity(self, data):
        """
            Check whether given data can be processed by this event. 
            Parameters:
                data    -    data array (DataArray) or measurement (Measurement)
            Output:
                True if yes
        """
        # Insert here tests that will tell whether the given data is compatible or not with this event
        return ScanEvent.check_validity(self, data)
    
    def get_icon(self):
        """
            Return scan event icon.
            Output:
                16x16 icon (wx.Bitmap)
        """
        import wx
        from terapy.core import icon_path
        # Place your custom icon where needed and change the path accordingly
        return wx.Image(icon_path + "empty.png").ConvertToBitmap()
