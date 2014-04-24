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

    Linear zig-zag scan event class

"""

from terapy.scan.scan_s import Scan
from numpy import linspace
from time import sleep

class Scan_ZZ(Scan):
    """
    
        Linear zig-zag scan event class

        Scan given axis device between two values in a given number of steps.
    
    """
    __extname__ = "Zig-zag scan"
    def __init__(self, parent = None):
        Scan.__init__(self, parent)
        self.axis = 0
        self.min = 0.0
        self.max = 25.6
        self.N = 257
        self.dv = 0.1
        self.fwd = True # start in forward direction
        self.propNames = ["Axis","Minimum","Maximum","# Steps","Step"]
        self.is_loop = True
    
    def refresh(self):
        Scan.refresh(self)
        self.fwd = True
    
    def run(self, data):
        self.itmList = self.get_children()
        ax = self.axlist[self.axis]
        ax.prepareScan()
        # scan selected axis from min to max
        coords = linspace(self.min,self.max,self.N)
        if self.fwd:
            n=-1
            while self.can_run and n<self.N-1:
                n+=1
                ax.goTo(coords[n])
                while (ax.get_motion_status() != 0 and self.can_run):
                    sleep(0.01)
                data.SetCoordinateValue(self.m_ids, ax.pos()) # read axis position
                self.run_children(data)
                data.Increment(self.m_ids)
            data.Decrement(self.m_ids)
            data.DecrementScanDimension(self.m_ids)
        else:
            n=self.N
            data.SetScanPosition(self.m_ids,self.N-1)
            while self.can_run and n>0:
                n-=1
                ax.goTo(coords[n])
                while (ax.get_motion_status() != 0 and self.can_run):
                    sleep(0.01)
                data.SetCoordinateValue(self.m_ids, ax.pos()) # read axis position
                self.run_children(data)
                data.Decrement(self.m_ids)
            data.Increment(self.m_ids)
            data.DecrementScanDimension(self.m_ids)
        self.fwd = not(self.fwd)
        return True
