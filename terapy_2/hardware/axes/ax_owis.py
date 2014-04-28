#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010-2013 Daniel Dietze, 2013-2014  Vincent Paeder
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

	Device driver for OWIS PS10 motion controller
 
"""

from terapy.hardware.axes.base import AxisDevice
from wx import GetTextFromUser
from time import sleep

try:
	import owis
	_support_OWIS = True
except:
	_support_OWIS = False

# OWIS PS10 controller
if _support_OWIS == True:
	class PS10(AxisDevice):		
		"""
		
			Device driver for OWIS PS10 motion controller
		 
		"""
		def __init__(self):
			AxisDevice.__init__(self)
			self.timeout = 2
			self.instr = None
			self.qtynames = "Position"
			self.units = "ps"
			self.psperunit = 1.0
			self.config = ["psperunit"]
			self.last_position = 0
		
		def initialize(self):
			# create device handle
			self.instr = owis.Owis()
			self.instr.connect_port(int(self.axis), int(self.address))
			self.name = self.instr.get_serial_number()
			# check whether device is responding
			print "initiated PS10 with S/N", self.name, "on port", self.address
			print "homing...", self.ID, ", axis", self.axis		
			self.instr.home_search()
		
		def reset(self):
			print "reinitialize.."
			self.instr.disconnect()
			self.instr.connect_port(int(self.axis), int(self.address))		
			print "homing...", self.ID, ", axis", self.axis	
			self.instr.home_search()
				
		def get_motion_status(self):		
			status = self.instr.motion_status()
			
			if(status == 0):
				return 0	# ready
			else:
				return 1	# moving or otherwise busy
				
		def stop(self):
			self.instr.stop()
		
		def goTo(self, position, wait = False):
			if(self.get_motion_status() != 0):
				self.stop()
			print self.ID, ": goto: ", position
			units = position / self.psperunit
			self.instr.move_abs(units)
			if(wait == True):
				while(self.get_motion_status() != 0 ):
					sleep(0.02)
			
		def jog(self, step):
			if(self.get_motion_status() != 0):
				self.stop()
			units = step / self.psperunit
			self.instr.move_rel(units)
			while(self.get_motion_status() != 0):
				sleep(0.02)
			return self.pos()
		
		def home(self):
			if(self.get_motion_status() != 0):
				self.stop()
			self.instr.home
		
		def pos(self):		
			try:
				units = self.instr.get_position()			
				self.last_position = units
			except:
				print "ERROR while reading position!"
				units = self.last_position
			return units * self.psperunit

		def configure(self):
			value = GetTextFromUser("Conversion factor for SI units per stage unit:", "PS10 Config", default_value=str(self.psperunit))
			if value != "":
				try:
					value = float(value)
				except:
					value = 1.0
				self.psperunit = value

		def detect(self):
			from serial import Serial
			retval = []
			if _support_OWIS == True:
				ax = 1
				instrOw = owis.Owis()
				for port in range(4, 10):		
					print "OWIS: test COM" + str(port) + ".."
					try:
						sleep(0.1)
						if instrOw.connect_port(ax, port) == 0:
							version = instrOw.get_serial_number()
							print " S/N: ", version
							print " axis:", ax
							retval.append([str(port),"Ax:"+str(ax)+" "+version,ax])
							ax = ax + 1
							instrOw.disconnect()
						ser = Serial("\\.\COM"+str(port))
						ser.close()
					except:			
						pass
			return retval
