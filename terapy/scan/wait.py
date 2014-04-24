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

    Wait scan event class

"""

from terapy.scan.base import ScanEvent
import wx
from time import sleep, time
from terapy.core import icon_path

class Wait(ScanEvent):
    """
    
        Wait scan event class
        
        Wait for specified amount of time.
    
    """
    __extname__ = "Wait"
    def __init__(self,parent=None):
        ScanEvent.__init__(self,parent)
        self.time = 100
        self.propNames = ["Time (ms)"]
        self.config = ["time"]
    
    def run(self, data):
        t0 = time()
        while time()-t0<self.time/1000.0 and self.can_run:
            sleep(0.01)
        return data
    
    def set(self, parent=None):
        dlg = wx.TextEntryDialog(parent, caption="Time to wait", message="Enter time to wait (ms):", defaultValue=str(self.time))
        if dlg.ShowModal() == wx.ID_OK:
            self.time = int(dlg.GetValue())
            if self.time<0:
                self.time = 0
            dlg.Destroy()
            return True
        else:
            dlg.Destroy()
            return False
    
    def populate(self):
        self.propNodes = [self.time]
        self.create_property_root()
        self.set_property_nodes(True)
    
    def set_property(self, pos, val):
        if pos==0:
            try:
                self.time = int(val)
            except:
                pass
            if self.time<0:
                self.time = 0
            self.propNodes[0] = self.time
            self.set_property_nodes(True)
        
    def get_icon(self):
        return wx.Image(icon_path + "event-wait.png").ConvertToBitmap()
