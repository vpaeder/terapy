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

	Device driver for Newport Agilis AG-UC motion controller
 
"""

from terapy.hardware.axes.base import AxisDevice
from time import sleep

class AGUC8(AxisDevice):
	"""
	
		Device driver for Newport Agilis AG-UC motion controller
	 
	"""
	def __init__(self):
		AxisDevice.__init__(self)
		self.timeout = 1.0
		self.qtynames = "Position"
		self.units = "um"
		self.instr = None
		self.umperunit = 0.05
		self.stepsize = 50
		self.config = ["umperunit","stepsize"]
	
	def initialize(self):
		# create device handle
		from visa import instrument, no_parity
		self.instr = instrument(self.address, baud_rate=921600, data_bits=8, stop_bits=1, parity=no_parity, timeout = 2.0, term_chars = "\r\n")
		print "homing...", self.ID, ", axis", self.axis
		self.instr.write("MR")
		#self.write("MV-4")
		while(self.get_motion_status() != 0):
			sleep(0.02)
		self.write("ZP")
		
	def write(self, cmd):
		cmdstr = str(self.axis) + cmd
		self.instr.write(cmdstr)
	
	def configure(self):
		print "Resetting position counter..."
		self.write("ZP")
	
	def reset(self):
		print "reinitialize.."
		self.write("ZP")
	
	def ask(self, cmd):
		cmdstr = str(self.axis) + cmd
		result = ""
		while(result == "" or result[0:len(cmdstr)] != cmdstr):
			result = self.instr.ask(cmdstr)
		return result[3:]
		
	def jog(self, step):
		if(self.get_motion_status() != 0):
			self.stop()
		self.write("SU" + str(self.stepsize))
		self.write("SU" + str(-self.stepsize))
		units = step / self.umperunit / self.stepsize
		self.write("PR" + str(int(units)))
		while(self.get_motion_status() != 0):
			sleep(0.02)
		return self.pos()
	
	def get_motion_status(self):
		status = self.ask("TS")
		status = int(status[-2:])
		return status
	
	def pos(self):
		steps = self.ask("TP")
		steps = float(steps)
		pos = steps*self.umperunit*self.stepsize
		return pos
	
	def stop(self):
		self.write("ST")
	
	def goTo(self, position, wait = False):
		self.write("SU" + str(self.stepsize))
		self.write("SU" + str(-self.stepsize))
		if(self.get_motion_status() != 0):
			self.stop()
		print "goto:", position
		position = position - self.pos()
		units = position / self.umperunit / self.stepsize
		self.write("PR" + str(int(units)))
		if(wait == True):
			while(self.get_motion_status() != 0 ):
				sleep(0.02)

	def detect(self):
		try:
			from visa import get_instruments_list, instrument, no_parity
		except:
			return []
		
		devlist = get_instruments_list()
		retval = []
		for handle in devlist:
			if (handle.find("COM") != -1):
				try:
					instr  = instrument(handle, baud_rate=921600, data_bits=8, stop_bits=1, parity=no_parity, timeout = 0.1, term_chars = "\r\n")
					version = instr.ask("VE")
				except:
					version = ""
				if (version.find("AG-UC8") != -1 ):
					for ax in range(1,5): # motion controller - probe axes
						try:						
							print "probe AG-UC8 axis ", ax
							ID = instr.ask(str(ax) + " TS")[3:]
							err = int(instr.ask("TE")[-1])
							print ID
							if(ID != "" and err == 0):
								retval.append([handle,"Ax:"+str(ax)+" "+version,ax])
							else:
								print "Error "+err
						except:
							print "exception"
		return retval
