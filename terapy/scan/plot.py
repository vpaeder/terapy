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

    Plot scan event class

"""

from terapy.scan.base import ScanEvent
import wx
from terapy.core import icon_path, refresh_delay
from wx.lib.pubsub import setupkwargs
from wx.lib.pubsub import pub
from time import time

class Plot(ScanEvent):
    """
    
        Plot scan event class
        
        Plot given data to available plot canvas.
    
    """
    __extname__ = "Plot"
    def __init__(self,parent=None):
        ScanEvent.__init__(self,parent)
        self.is_display = True
        self.canvas = None
        self.can_plot = True
        self.auto_refresh = True
        self.clock = 0
        pub.subscribe(self.set_canvas,"broadcast_canvas")
        pub.subscribe(self.set_refresh,"broadcast_refresh")
    
    def refresh(self):
        ScanEvent.refresh(self)
        pub.sendMessage("request_canvas")
    
    def set_canvas(self, inst=None):
        self.canvas = inst
    
    def set_refresh(self, inst=None):
        self.auto_refresh = inst
    
    def run(self, data):
        arr = data.data[self.m_id]
        wx.CallAfter(self.plot,arr)
        return True
    
    def get_icon(self):
        return wx.Image(icon_path + "event-display.png").ConvertToBitmap()
    
    def plot(self, arr):
        if arr.plot==None:
            pub.sendMessage("request_canvas")
            arr.plot = self.canvas.AddPlot(array=arr)
            pub.sendMessage("plot.color_change")
            arr.plot.SetName(arr.name)
        arr.plot.SetData(arr)
        
        if time() - self.clock > refresh_delay and self.auto_refresh:
            arr.plot.Update()
            self.clock = time()
    
    def check_validity(self, data):
        # can process only 1D and 2D arrays
        v = len(data.shape)
        if v<1 or v>2:
            return False
        else:
            return True
        