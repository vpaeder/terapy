#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2012  Daniel Dietze
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

	ADWin Lock-in settings dialog.

"""

# wx for general GUI
import wx
from math import pi

class ADWinLockInConfig(wx.Dialog):
	"""
	
		ADWin Lock-in settings dialog.
	
	"""
	# config is the configuration dictionary from the input device class for the ADWinLIA
	def __init__(self, dev):
		wx.Dialog.__init__(self, None, -1, 'ADWinLockIn Configuration')		

		self.propertymap = {"amplification" : [0, 1, 2, 3], 
			"mode" : [0, 1],
			"flock" : [0, 1, 2, 3],
			"signal" : [0, 1, 2, 3]
			}
		
		# add controls
		self.range_label = wx.StaticText(self, -1, "Input Range")
		self.range = wx.Choice(self, -1, choices=["20V", "10V", "5V", "2.5V"])
		
		self.mode_label = wx.StaticText(self, -1, "Ref.source")
		self.mode = wx.Choice(self, -1, choices=["External (CH2)", "Internal"])
		
		self.flock_mode_label = wx.StaticText(self, -1, "Lock to")
		self.flock_mode = wx.Choice(self, -1, choices=["CH1", "CH2", "CH1 - CH2", "CH1 + CH2"])
				
		self.CH1_frequency_label = wx.StaticText(self, -1, "CH1 freq. out (Hz)")
		self.CH1_frequency = wx.TextCtrl(self, -1, "10000.0", style = wx.TE_RIGHT)
		#	self.CH1_amplitude_label = wx.StaticText(self, -1, "CH1 amp. out (V)")
		#	self.CH1_amplitude = wx.TextCtrl(self, -1, "0.01", style = wx.TE_RIGHT)
		
		self.CH2_frequency_label = wx.StaticText(self, -1, "CH2 freq. out (Hz)")
		self.CH2_frequency = wx.TextCtrl(self, -1, "3000.0", style = wx.TE_RIGHT)
		self.CH2_amplitude_label = wx.StaticText(self, -1, "CH2 amp. out (V)")
		self.CH2_amplitude = wx.TextCtrl(self, -1, "4.0", style = wx.TE_RIGHT)
		
		self.reftrigger_label = wx.StaticText(self, -1, "Trigger Level (V)")
		self.reftrigger = wx.TextCtrl(self, -1, "2.0", style = wx.TE_RIGHT)
		
		self.holdoff_label = wx.StaticText(self, -1, "Wait (s)")
		self.holdoff = wx.TextCtrl(self, -1, "0.0", style = wx.TE_RIGHT)
		
		self.avg_time_label = wx.StaticText(self, -1, "Int.time (ms)")
		self.avg_time = wx.TextCtrl(self, -1, "300.0", style = wx.TE_RIGHT)
		
		self.phase_label = wx.StaticText(self, -1, "Lock-In Phase (deg)")
		self.phase = wx.TextCtrl(self, -1, "0.0", style = wx.TE_RIGHT)
		
		self.signal_label = wx.StaticText(self, -1, "Signal")
		self.signal = wx.Choice(self, -1, choices=["X", "Y", "R", "PHI"])

		self.autophase = wx.CheckBox(self, -1, "Auto-Phase")
		
		# dialog buttons
		self.cancel_button = wx.Button(self, wx.ID_CANCEL, "Cancel")		
		self.ok_button = wx.Button(self, wx.ID_OK, "Apply")
		
		# arrange objects and set layout
		self.__set_properties(dev)
		self.__do_layout()
		
		# event bindings
		self.Bind(wx.EVT_CHOICE, self.onMode, self.mode)
		
		self.reftrigger.Bind(wx.EVT_KILL_FOCUS, self.onRefTrigger, self.reftrigger)
		self.CH1_frequency.Bind(wx.EVT_KILL_FOCUS, self.onCH1Frequency, self.CH1_frequency)
		#self.CH1_amplitude.Bind(wx.EVT_KILL_FOCUS, self.onCH1Amplitude, self.CH1_amplitude)		
		self.CH2_frequency.Bind(wx.EVT_KILL_FOCUS, self.onCH2Frequency, self.CH2_frequency)
		self.CH2_amplitude.Bind(wx.EVT_KILL_FOCUS, self.onCH2Amplitude, self.CH2_amplitude)
		self.holdoff.Bind(wx.EVT_KILL_FOCUS, self.onHoldoff, self.holdoff)
		self.avg_time.Bind(wx.EVT_KILL_FOCUS, self.onAvgTime, self.avg_time)
		self.phase.Bind(wx.EVT_KILL_FOCUS, self.onPhase, self.phase)
		
		
	# set properties and layout
	def __set_properties(self, dev):				
		self.range.SetSelection(self.propertymap['amplification'].index(dev.amplification))
		self.mode.SetSelection(self.propertymap['mode'].index(dev.mode))
		self.flock_mode.SetSelection(self.propertymap['flock'].index(dev.flock))
		self.signal.SetSelection(self.propertymap['signal'].index(dev.signal))		
		
		self.holdoff.SetValue(str(dev.holdoff))
		self.avg_time.SetValue(str(dev.inttime))
		self.phase.SetValue(str(dev.PHI * 180.0 / pi))
		
		self.CH1_frequency.SetValue(str(dev.CH1_f))
		#self.CH1_amplitude.SetValue(str(dev.CH1_A))
		self.CH2_frequency.SetValue(str(dev.CH2_f))
		self.CH2_amplitude.SetValue(str(dev.CH2_A))
		self.reftrigger.SetValue(str(dev.reftrigger))
		
		self.autophase.SetValue(False)
		
		self.enableIntControls()
		
	def __do_layout(self):
		main_sizer = wx.BoxSizer(wx.VERTICAL)
		hbox = wx.BoxSizer(wx.HORIZONTAL)	
		vbox = wx.BoxSizer(wx.VERTICAL)
		
		# lockin stuff	
		vbox1st = wx.StaticBox(self, -1, "Lock-In Parameters")
		vbox1 = wx.StaticBoxSizer(vbox1st, wx.VERTICAL)
		
		hbox6v1 = wx.BoxSizer(wx.HORIZONTAL)
		hbox6v1.Add(self.mode_label, 1, wx.ALL | wx.EXPAND, 2)
		hbox6v1.Add(self.mode, 1, wx.ALL | wx.EXPAND, 2)
		vbox1.Add(hbox6v1, 0, wx.EXPAND)
		hbox7v1 = wx.BoxSizer(wx.HORIZONTAL)
		hbox7v1.Add(self.flock_mode_label, 1, wx.ALL | wx.EXPAND, 2)
		hbox7v1.Add(self.flock_mode, 1, wx.ALL | wx.EXPAND, 2)
		vbox1.Add(hbox7v1, 0, wx.EXPAND)
		hbox1v1 = wx.BoxSizer(wx.HORIZONTAL)
		hbox1v1.Add(self.holdoff_label, 1, wx.ALL | wx.EXPAND, 2)
		hbox1v1.Add(self.holdoff, 1, wx.ALL | wx.EXPAND, 2)
		vbox1.Add(hbox1v1, 0, wx.EXPAND)
		hbox2v1 = wx.BoxSizer(wx.HORIZONTAL)
		hbox2v1.Add(self.avg_time_label, 1, wx.ALL | wx.EXPAND, 2)
		hbox2v1.Add(self.avg_time, 1, wx.ALL | wx.EXPAND, 2)
		vbox1.Add(hbox2v1, 0, wx.EXPAND)
		hbox3v1 = wx.BoxSizer(wx.HORIZONTAL)
		hbox3v1.Add(self.phase_label, 1, wx.ALL | wx.EXPAND, 2)
		hbox3v1.Add(self.phase, 1, wx.ALL | wx.EXPAND, 2)
		vbox1.Add(hbox3v1, 0, wx.EXPAND)
		hbox4v1 = wx.BoxSizer(wx.HORIZONTAL)
		hbox4v1.Add(self.signal_label, 1, wx.ALL | wx.EXPAND, 2)
		hbox4v1.Add(self.signal, 1, wx.ALL | wx.EXPAND, 2)
		vbox1.Add(hbox4v1, 0, wx.EXPAND)
		hbox5v1 = wx.BoxSizer(wx.HORIZONTAL)
		hbox5v1.Add(self.autophase, 1, wx.ALL | wx.EXPAND, 2)
		vbox1.Add(hbox5v1, 0, wx.EXPAND)
		
		# input stuff
		vbox2st = wx.StaticBox(self, -1, "Input Channels")
		vbox2 = wx.StaticBoxSizer(vbox2st, wx.VERTICAL)
		hbox1v2 = wx.BoxSizer(wx.HORIZONTAL)
		hbox1v2.Add(self.range_label, 1, wx.ALL | wx.EXPAND, 2)
		hbox1v2.Add(self.range, 1, wx.ALL | wx.EXPAND, 2)
		vbox2.Add(hbox1v2, 0, wx.EXPAND)
		hbox2v2 = wx.BoxSizer(wx.HORIZONTAL)
		hbox2v2.Add(self.reftrigger_label, 1, wx.ALL | wx.EXPAND, 2)
		hbox2v2.Add(self.reftrigger, 1, wx.ALL | wx.EXPAND, 2)
		vbox2.Add(hbox2v2, 0, wx.EXPAND)
				
		# output stuff
		vbox3st = wx.StaticBox(self, -1, "Output Channels")
		vbox3 = wx.StaticBoxSizer(vbox3st, wx.VERTICAL)
		hbox1v3 = wx.BoxSizer(wx.HORIZONTAL)
		hbox1v3.Add(self.CH1_frequency_label, 1, wx.ALL | wx.EXPAND, 2)
		hbox1v3.Add(self.CH1_frequency, 1, wx.ALL | wx.EXPAND, 2)
		vbox3.Add(hbox1v3, 0, wx.EXPAND)
		# hbox2v3 = wx.BoxSizer(wx.HORIZONTAL)
		# hbox2v3.Add(self.CH1_amplitude_label, 1, wx.ALL | wx.EXPAND, 2)
		# hbox2v3.Add(self.CH1_amplitude, 1, wx.ALL | wx.EXPAND, 2)
		# vbox3.Add(hbox2v3, 0, wx.EXPAND)
		hbox3v3 = wx.BoxSizer(wx.HORIZONTAL)
		hbox3v3.Add(self.CH2_frequency_label, 1, wx.ALL | wx.EXPAND, 2)
		hbox3v3.Add(self.CH2_frequency, 1, wx.ALL | wx.EXPAND, 2)
		vbox3.Add(hbox3v3, 0, wx.EXPAND)
		hbox4v3 = wx.BoxSizer(wx.HORIZONTAL)
		hbox4v3.Add(self.CH2_amplitude_label, 1, wx.ALL | wx.EXPAND, 2)
		hbox4v3.Add(self.CH2_amplitude, 1, wx.ALL | wx.EXPAND, 2)
		vbox3.Add(hbox4v3, 0, wx.EXPAND)
		
		
		vbox.Add(vbox2, 0, wx.EXPAND)
		vbox.Add(vbox3, 0, wx.EXPAND)
		vbox.AddStretchSpacer()
		
		hbox.Add(vbox1, 0, wx.EXPAND)
		hbox.Add(vbox, 0, wx.EXPAND)
		
		main_sizer.Add(hbox, 0, wx.ALL | wx.EXPAND, 2)
		
		# dialog buttons
		buttonSizer = wx.BoxSizer(wx.HORIZONTAL)						
		buttonSizer.Add(self.cancel_button, 0, wx.ALL | wx.ALIGN_CENTER, 2)		
		buttonSizer.Add(self.ok_button, 0, wx.ALL | wx.ALIGN_CENTER, 2)				
		main_sizer.Add(buttonSizer, 0, wx.ALL | wx.ALIGN_CENTER, 2)
		
		# attach main sizer to panel to adjust element sizes
		self.SetAutoLayout(True)
		self.SetSizer(main_sizer)
		self.Fit()		
	
	def enableIntControls(self):
		b = self.mode.GetSelection() == 1		# b is False if external source is selected
		
		self.flock_mode.Enable(b)				# those are needed for internal
		self.CH1_frequency.Enable(b)
		#self.CH1_amplitude.Enable(b)
		self.CH2_frequency.Enable(b)
		self.CH2_amplitude.Enable(b)
		self.reftrigger.Enable(not b)			# this is needed for external		
	
	def onMode(self, event):
		self.enableIntControls()
	
	def onRefTrigger(self, event):
		if(float(self.reftrigger.GetValue()) < -10.0):
			self.reftrigger.SetValue("-10.0")
		if(float(self.reftrigger.GetValue()) > 10.0):
			self.reftrigger.SetValue("10.0")
	
	def onCH1Frequency(self, event):
		if(float(self.CH1_frequency.GetValue()) < 0.0):
			self.CH1_frequency.SetValue("0.0")
		if(float(self.CH1_frequency.GetValue()) > 500000.0):
			self.CH1_frequency.SetValue("500000.0")
			
	# def onCH1Amplitude(self, event):
		# if(float(self.CH1_amplitude.GetValue()) < -10.0):
			# self.CH1_amplitude.SetValue("-10.0")
		# if(float(self.CH1_amplitude.GetValue()) > 10.0):
			# self.CH1_amplitude.SetValue("10.0")
	
	def onCH2Frequency(self, event):
		if(float(self.CH2_frequency.GetValue()) < 0.0):
			self.CH2_frequency.SetValue("0.0")
		if(float(self.CH2_frequency.GetValue()) > 500000.0):
			self.CH2_frequency.SetValue("500000.0")
			
	def onCH2Amplitude(self, event):
		if(float(self.CH2_amplitude.GetValue()) < -10.0):
			self.CH2_amplitude.SetValue("-10.0")
		if(float(self.CH2_amplitude.GetValue()) > 10.0):
			self.CH2_amplitude.SetValue("10.0")
			
	def onHoldoff(self, event):
		if(float(self.holdoff.GetValue()) < 0.0):
			self.holdoff.SetValue("0.0")
					
	def onAvgTime(self, event):
		if(float(self.avg_time.GetValue()) < 1):
			self.avg_time.SetValue("1.0")
	
	def onPhase(self, event):
		self.phase.SetValue(str(float(self.phase.GetValue()) % 180.0))
		
	def get_configuration(self,dev):
		
		dev.CH1_f = float(self.CH1_frequency.GetValue())
		#dev.CH1_A = float(self.CH1_amplitude.GetValue())
		dev.CH2_f = float(self.CH2_frequency.GetValue())
		dev.CH2_A = float(self.CH2_amplitude.GetValue())
		dev.reftrigger = float(self.reftrigger.GetValue())
		
		dev.PHI = float(self.phase.GetValue()) * pi / 180.0
		dev.holdoff = float(self.holdoff.GetValue())
		dev.inttime = float(self.avg_time.GetValue())
		
		dev.amplification = self.propertymap['amplification'][self.range.GetSelection()]
		dev.signal = self.propertymap['signal'][self.signal.GetSelection()]
		dev.mode = self.propertymap['mode'][self.mode.GetSelection()]
		dev.flock = self.propertymap['flock'][self.flock_mode.GetSelection()]
