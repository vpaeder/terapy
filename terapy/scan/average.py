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

    Average multiple scans class.

"""
    
from terapy.scan.base import ScanEvent
from terapy.core.dataman import Measurement, DataArray
from terapy.core import icon_path
import wx
from numpy import zeros

class Average(ScanEvent):
    """
    
        Average multiple scans class.
        
        Average multiple scans into one.
    
    """
    __extname__ = "Average"
    def __init__(self,parent=None):
        ScanEvent.__init__(self,parent)
        self.avg = 5
        self.propNames = ["Count"]
        self.is_loop = True
        self.config = ["avg"]
    
    def run(self, data):
        self.itmList = self.get_children()
        n=0
        # store original data
        data0 = Measurement()
        data0.data = []
        for m_id in self.m_ids:
            data0.data.append(DataArray())
            if hasattr(data.data[m_id].data,'__iter__'):
                data0.data[m_id].data = zeros(data.data[m_id].data.shape)
            else:
                data0.data[m_id].data = 0
        # repeat sub-sequence
        while n<self.avg and self.can_run:
            n+=1
            self.run_children(data)
            for m_id in self.m_ids:
                data0.data[m_id].data = data0.data[m_id].data + data.data[m_id].data
            data.Increment(self.m_ids)
        for m_id in self.m_ids:
            data.data[m_id].data = data0.data[m_id].data/self.avg
        return data

    def get_operation_count(self):
        return self.avg
    
    def set(self, parent=None):
        dlg = wx.TextEntryDialog(parent, caption="Number of repetitions", message="Enter number of repetitions:", defaultValue=str(self.avg))
        if dlg.ShowModal() == wx.ID_OK:
            self.avg = int(dlg.GetValue())
            if self.avg<1:
                self.avg = 1
            dlg.Destroy()
            return True
        else:
            dlg.Destroy()
            return False
    
    def populate(self):
        self.propNodes = [self.avg]
        self.create_property_root()
        self.set_property_nodes(True)

    def set_property(self, pos, val):
        if pos==0:
            try:
                self.avg = int(val)
            except:
                pass
            if self.avg<1:
                self.avg = 1
            self.propNodes[0] = self.avg
            self.set_property_nodes(True)
        
    def get_icon(self):
        return wx.Image(icon_path + "event-loop.png").ConvertToBitmap()
