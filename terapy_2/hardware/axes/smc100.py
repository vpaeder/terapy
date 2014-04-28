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

	Device driver for Newport SMC100 motion controller
 
"""

from terapy.hardware.axes.base import AxisDevice
from wx import GetTextFromUser
from time import sleep

class SMC100(AxisDevice):
	"""
	
		Device driver for Newport SMC100 motion controller
	 
	"""
	def __init__(self):
		AxisDevice.__init__(self)
		self.timeout = 2
		self.qtynames = "Position"
		self.units = "ps"
		self.instr = None
		self.psperunit = 6.6713
		self.config = ["psperunit"]
		self.last_position = 0
	
	def initialize(self):
		# create device handle
		from visa import instrument, no_parity
		self.instr = instrument(self.address, baud_rate=57600, data_bits=8, stop_bits=1, parity=no_parity, timeout = 1.0, term_chars = "\r\n")
		# check whether device is responding
		print "initiated", self.instr.ask(str(self.axis) + "VE"), "on port", self.address
		print "homing...", self.ID, ", axis", self.axis		
		self.write("OR")
		
	def reset(self):
		print "reinitialize.."
		self.initialize()
		# reset
		#self.write("RS")
		# home search
		#print "homing...", self.ID, ", axis", self.axis	
		#self.write("OR")
	
	def ask(self, cmd):
		cmdstr = str(self.axis) + cmd
		result = ""
		while(result == "" or result[0:len(cmdstr)] != cmdstr):
			result = self.instr.ask(cmdstr)
		return result[3:]
		
	def write(self, cmd):
		cmdstr = str(self.axis) + cmd
		self.instr.write(cmdstr)
		
	def get_motion_status(self):		
		status = self.ask("TS")
		status = status[-2:]
		if(status == "28"):
			return 1	# moving
		elif(status == "1E"):
			return 2	# homing
		elif(status == "32" or status == "33" or status == "34"):
			return 0	# ready
		else:
			print "STAGE STATUS:", status
			return 3
		
	def stop(self):
		self.write("ST")
	
	def goTo(self, position, wait = False):
		if(self.get_motion_status() != 0):
			self.stop()
		print "goto:", position
		units = position / self.psperunit
		self.write("PA" + str(units))
		if(wait == True):
			while(self.get_motion_status() != 0 ):
				sleep(0.01)
		
	def jog(self, step):
		if(self.get_motion_status() != 0):
			self.stop()
		units = step / self.psperunit
		#self.instr.write(str(self.axis) + "PR" + str(units))
		self.write("PR" + str(units))
		while(self.get_motion_status() != 0):
			sleep(0.01)
		return self.pos()
	
	def home(self):
		if(self.get_motion_status() != 0):
			self.stop()
		self.goTo(0)
	
	def pos(self):
		try:
			units = self.ask("TP")		
			units = float(units)
			self.last_position = units
		except:
			print "ERROR while reading position!"
			units = self.last_position
		return units * self.psperunit

	def configure(self):
		value = GetTextFromUser("Conversion factor for ps per unit (can be negative, 1mm in air (single pass) = 6.6713ps):", "SMC100 Config", default_value=str(self.psperunit))
		if value != "":
			try:
				value = float(value)
			except:
				value = 6.6713
			self.psperunit = value

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
					instr = instrument(handle, baud_rate=57600, data_bits=8, stop_bits=1, parity=no_parity, timeout = 0.5, term_chars = "\r\n")
					for ax in range(1,4): # motion controller - probe axes, probe only 1 to 4 (SMC supports up to 31 controllers!)				
						try:
							version = instr.ask(str(ax) + "VE") # query controllers, each controller can handle 1 axis 
							if (version.find("SMC") != -1):
								retval.append([handle,"Ax:"+str(ax)+" "+version,ax])
						except:
							pass
				except:
					pass
		return retval
