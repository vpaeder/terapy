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

    Sequence scan event class

"""

from terapy.scan.base import ScanEvent
import wx
from terapy.core import icon_path
from wx.lib.pubsub import Publisher as pub

class Sequence(ScanEvent):
    """
    
        Sequence scan event class
        
        Scan event sequence.
    
    """
    __extname__ = "Sequence"
    def __init__(self,parent=None):
        ScanEvent.__init__(self,parent)
        self.is_root = True
    
    def run(self, data):
        # loop through children
        itmlist = self.get_children()
        for x in itmlist:
            if self.can_run:
                ev = self.host.GetItemData(x).GetData()
                if ev.is_active:
                    if ev.is_display or ev.is_save:
                        ev.run(data)
                    elif ev.is_input:
                        ev.run(data)
                    elif ev.is_axis:
                        ev.run([])
                    elif ev.is_loop:
                        data.ResetCounter(self.m_ids) 
                        ev.run(data)
        pub.sendMessage("scan.stop")
        return True
    
    def get_icon(self):
        return wx.Image(icon_path + "event-list.png").ConvertToBitmap()
