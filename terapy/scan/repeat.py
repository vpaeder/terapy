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

    Repeat measurement scan event class

"""

from terapy.scan.base import ScanEvent
import wx
from terapy.core import icon_path

class Repeat(ScanEvent):
    """
    
        Repeat measurement scan event class
        
        Repeat measurement multiple times and store results separately.
    
    """
    __extname__ = "Repeat"
    def __init__(self,parent=None):
        ScanEvent.__init__(self,parent)
        self.N = 5
        self.propNames = ["Count"]
        self.is_loop = True
        self.config = ["N"]
    
    def run(self, data):
        self.itmList = self.get_children()
        n=0
        while n<self.N and self.can_run:
            n+=1
            self.run_children(data)
            data.Increment(self.m_ids)
                    
        return data

    def get_operation_count(self):
        return self.N

    def set(self, parent=None):
        dlg = wx.TextEntryDialog(parent, caption="Number of repetitions", message="Enter number of repetitions:", defaultValue=str(self.N))
        if dlg.ShowModal() == wx.ID_OK:
            self.N = int(dlg.GetValue())
            if self.N<1:
                self.N = 1
            dlg.Destroy()
            return True
        else:
            dlg.Destroy()
            return False
    
    def populate(self):
        self.propNodes = [self.N]
        self.create_property_root()
        self.set_property_nodes(True)

    def set_property(self, pos, val):
        if pos==0:
            try:
                self.N = int(val)
            except:
                pass
            if self.N<1:
                self.N = 1
            self.propNodes[0] = self.N
            self.set_property_nodes(True)
        
    def get_icon(self):
        return wx.Image(icon_path + "event-loop.png").ConvertToBitmap()
