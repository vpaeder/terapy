#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2014  Vincent Paeder
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

	Device driver for Toptica FemtoPro laser
 
"""

from terapy.hardware.axes.base import AxisDevice, AxisWidget
from terapy.hardware.interfaces import comports, get_port
from time import sleep
from toptica_ffpro_w0 import FFProWidget
from toptica_ffpro_w1 import FFProOptimizerWidget

class TOPTFFPro(AxisDevice):
	"""
	
		Device driver for Toptica FemtoPro laser
	 
	"""
	def __init__(self):
		AxisDevice.__init__(self)
		self.timeout = 1.0
		self.qtynames = "Position"
		self.units = "um"
		self.instr = None
		self.auto_optimize = False
		self.arms = 1
		self.config = ["auto_optimize"]
		self.instr = None
		self.prism = None
		self.mode_lock = 0
		self.optimizer = OptimizerSettings()
		self.shg = OptionalFeature()
		self.tnir = OptionalFeature()
		self.tvis = OptionalFeature()
		self.communicating = False
	
	def __del__(self):
		if self.instr!=None:
			self.instr.close()
			while self.instr.isOpen():
				sleep(0.01)
	
	def write(self, cmd):
		self.instr.flush()
		self.instr.write(cmd+'\r\n')
	
	def ask(self, cmd):
		while self.communicating:
			sleep(0.001)
		
		self.communicating = True
		self.write(cmd)
		rcnt = 0
		t0 = 0.0
		rlines = []
		curline = ""
		# wait for answer to current command
		while curline.find(cmd)<0:
			rcnt = self.instr.inWaiting()
			if rcnt>0:
				curline = self.instr.readline()
		# wait for answer end
		while curline!=">>> \r\n":
			rcnt = self.instr.inWaiting()
			if rcnt>0:
				curline = self.instr.readline()
				rlines.append(curline.strip())
			sleep(0.001)
			t0+=0.001
			if t0>self.instr.timeout:
				break
		self.instr.flush()
		self.communicating = False
		return rlines
	
	def initialize(self):
		# create device handle
		self.instr = get_port(self.address)
		self.axis = int(self.axis)
		if self.instr==None:
			return
		
		self.instr.timeout = 2
		if not(self.instr.isOpen()):
			self.instr.baudrate = 115200
			self.instr.open()
			sleep(0.5)
		
		self.set_prism_type()
		
		# if the device has slaves, connect them
		self.write("ffpro.connect_slaves()")
	
	def set_prism_type(self):
		isSi = bool(self.ask("hasattr(ffpro.arm%d,'axSi')" % self.axis)[0])
		if isSi:
			self.prism = "axSi"
		else:
			self.prism = "axSF10"
	
	def configure(self):
		print "Turning laser on..."
		self.write("ffpro.arm%d.on()" % self.axis)
		print "Setting power to 100%..."
		self.write("ffpro.arm%d.level=1.0" % self.axis)
		print "Optimizing..."
		self.write("ffpro.arm%d.optimizer.auto=0" % self.axis)
		self.write("ffpro.arm%d.optimizer.scan()" % self.axis)
		self.write("ffpro.arm%d.optimizer.optimize()" % self.axis)
		self.write("ffpro.arm%d.optimizer.auto=%d" % (self.axis,self.auto_optimize))
	
	def reset(self):
		print "Reinitialize.."
		self.stop()
		self.configure()
	
	def get_motion_status(self):
		arrived = not(bool(int(self.ask("ffpro.arm%d.%s.arrived" % (self.axis, self.prism))[0])))
		available = not(bool(int(self.ask("ffpro.arm%d.%s.available" % (self.axis, self.prism))[0])))
		return (arrived and available) 
	
	def pos(self):
		armpos = self.ask("ffpro.arm%d.%s.pos" % (self.axis, self.prism))
		return float(armpos[0])
	
	def update_laser_status(self):
		self.mode_lock = int(self.ask("ffpro.osci.modelock")[0])
		self.amp_level = float(self.ask("ffpro.arm%d.level" % self.axis)[0])
		self.rep_rate = int(self.ask("ffpro.osci.reprate")[0])
		
		self.shg.installed = bool(int(self.ask("ffpro.arm%d.shg.installed" % self.axis)[0]))
		self.tnir.installed = bool(int(self.ask("ffpro.arm%d.tnir.installed" % self.axis)[0])) 
		self.tvis.installed = bool(int(self.ask("ffpro.arm%d.tvis.installed" % self.axis)[0]))
		
		if self.shg.installed:
			self.shg.power = float(self.ask("ffpro.arm%d.shg.power" % self.axis)[0])
			self.shg.oven_notok = int(self.ask("ffpro.arm%d.shg.oven.notok" % self.axis)[0])
			self.shg.oven_settemp = float(self.ask("ffpro.arm%d.shg.oven.settemp" % self.axis)[0])
			self.shg.oven_temp = float(self.ask("ffpro.arm%d.shg.oven.temp" % self.axis)[0])
		
		if self.tnir.installed:
			self.tnir.intensity = float(self.ask("ffpro.arm%d.tnir.intensity" % self.axis)[0])
			self.tnir.oven_notok = int(self.ask("ffpro.arm%d.tnir.oven.notok" % self.axis)[0])
			self.tnir.oven_settemp = float(self.ask("ffpro.arm%d.tnir.oven.settemp" % self.axis)[0])
			self.tnir.oven_temp = float(self.ask("ffpro.arm%d.tnir.oven.temp" % self.axis)[0])
		
		if self.tvis.installed:
			self.tvis.intensity = float(self.ask("ffpro.arm%d.tvis.intensity" % self.axis)[0])
			self.tvis.oven_notok = int(self.ask("ffpro.arm%d.tvis.oven.notok" % self.axis)[0])
			self.tvis.oven_settemp = float(self.ask("ffpro.arm%d.tvis.oven.settemp" % self.axis)[0])
			self.tvis.oven_temp = float(self.ask("ffpro.arm%d.tvis.oven.temp" % self.axis)[0])
	
	def update_optimizer_status(self):
		self.optimizer.automatic = bool(self.ask("ffpro.arm%d.optimizer.auto" % self.axis)[0])
		self.optimizer.blocked = bool(self.ask("ffpro.arm%d.optimizer.block" % self.axis)[0])
		self.optimizer.busy = bool(self.ask("ffpro.arm%d.optimizer.busy" % self.axis)[0])
		self.optimizer.minpower = float(self.ask("ffpro.arm%d.optimizer.minpower" % self.axis)[0])
		self.optimizer.setpoint = float(self.ask("ffpro.arm%d.optimizer.setpoint" % self.axis)[0])
		self.optimizer.threshold = float(self.ask("ffpro.arm%d.optimizer.threshold" % self.axis)[0])
		self.optimizer.tolerance = float(self.ask("ffpro.arm%d.optimizer.tolerance" % self.axis)[0])
	
	def stop(self):
		pass
		#print "Turning laser off..."
		#self.write("arm%d.off()" % self.axis)
	
	def goTo(self, position, wait = False):
		self.ask("ffpro.arm%d.%s.stop()" % (self.axis, self.prism))
		while self.get_motion_status():
			sleep(0.01)
		# check min and max positions
		scanmin = self.ask("ffpro.arm%d.%s.min" % (self.axis,self.prism))
		scanmin = float(scanmin[0])
		scanmax = self.ask("ffpro.arm%d.%s.max" % (self.axis,self.prism))
		scanmax = float(scanmax[0])
		if position<scanmin or position>scanmax:
			print "WARNING: position outside bounds!"
			position = max([min([scanmax,position]),scanmin])
		
		print "set prism position (um) to:", position
		if wait:
			self.write("ffpro.arm%d.%s.moveabswait(%f)" % (self.axis, self.prism, position))
		else:
			self.write("ffpro.arm%d.%s.target = %f" % (self.axis, self.prism, position))
	
	def jog(self, step, wait = False):
		self.ask("ffpro.arm%d.%s.stop()" % (self.axis, self.prism))
		while self.get_motion_status():
			sleep(0.01)
		
		print "move prism position (um) by:", step
		if wait:
			self.write("ffpro.arm%d.%s.moverelwait(%f)" % (self.axis, self.prism, step))
		else:
			self.write("ffpro.arm%d.%s.moverel(%f)" % (self.axis, self.prism, step))
	
	def detect(self):
		retval = []
		for port in comports:
			self.instr = port
			self.instr.timeout = 2
			self.instr.baudrate = 115200
			try:
				if not(self.instr.isOpen()):
					self.instr.open()
					sleep(0.5)
				print "port %s open... probing" % port.port
				# probe for FemtoFiber Pro
				rep = self.ask("ffpro.serial")
				if rep[0].find("FFpro")>=0:
					version = rep[0].replace("'","")
					# check how many axes are available
					narms = int(self.ask("len(ffpro.arms)")[0])
					for ax in range(narms):
						retval.append([port.port,"%s, arm %d" %(version,ax),ax])
					# close device
				self.instr.close()
			except:
				try:
					self.instr.close()
				except:
					pass
		return retval

	def widget(self, parent=None):
		"""
		
			Return widget for graphical device control.
			
			Parameters:
				parent	-	parent window (wx.Window)
			
			Output:
				widget (wx.Frame)
		
		"""
		#try:
		
		return [FFProWidget(parent,title=self.ID + ": " +self.name, instr = self),AxisWidget(parent,qtyname=self.qtynames, units=self.units, title=self.ID + ": " +self.name, pos = str(self.pos()), axis = self),FFProOptimizerWidget(parent,title=self.ID + ": " +self.name, instr = self)]
		#except:
		#	return None

class OptionalFeature():
	def __init__(self):
		self.installed = False
		self.power = 0.0 # for SHG
		self.oven_notok = 0 # for SHG, TNIR, TVIS
		self.oven_settemp = 0 # for SHG, TNIR, TVIS
		self.oven_temp = 0 # for SHG, TNIR, TVIS
		self.intensity = 0 # for TNIR, TVIS

class OptimizerSettings():
	def __init__(self):
		self.automatic = False
		self.blocked = False
		self.busy = False
		self.minpower = 0.0
		self.setpoint = 0.0
		self.threshold = 0.0
		self.tolerance = 0.0

