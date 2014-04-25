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

	Relative linear zig-zag scan event class

"""

from terapy.scan.scan_sr import ScanRelative
from numpy import linspace
from time import sleep

class ScanRelative_ZZ(ScanRelative):
	"""
	
		Relative linear zig-zag scan event class

		Scan given axis device a given number of times with specified step.
	
	"""
	__extname__ = "Relative zig-zag scan"
	def __init__(self, parent = None):
		ScanRelative.__init__(self, parent)
		self.axis = 0
		self.N = 257
		self.dv = 0.1
		self.fwd = True # start in forward direction
		self.propNames = ["Axis","# Steps","Step"]
		self.is_loop = True
	
	def refresh(self):
		ScanRelative.refresh(self)
		self.fwd = True
	
	def run(self, data):
		self.itmList = self.get_children()
		ax = self.axlist[self.axis]
		ax.prepareScan()
		p0 = ax.pos()
		if self.fwd:
			n=0
			data.SetScanPosition(self.m_ids,n)
			while self.can_run and n<self.N:
				ax.goTo(p0+n*self.dv)
				while (ax.get_motion_status() != 0 and self.can_run):
					sleep(0.01)
				data.SetCoordinateValue(self.m_ids, ax.pos()) # read axis position
				self.run_children(data)
				data.Increment(self.m_ids)
				n+=1
			data.Decrement(self.m_ids)
			data.DecrementScanDimension(self.m_ids)
		else:
			n=self.N-1
			data.SetScanPosition(self.m_ids,n)
			while self.can_run and n>=0:
				ax.goTo(p0+n*self.dv)
				while (ax.get_motion_status() != 0 and self.can_run):
					sleep(0.01)
				data.SetCoordinateValue(self.m_ids, ax.pos()) # read axis position
				self.run_children(data)
				data.Decrement(self.m_ids)
				n-=1
			data.Increment(self.m_ids)
			data.DecrementScanDimension(self.m_ids)
		self.fwd = not(self.fwd)
		return True
