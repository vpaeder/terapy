#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010-2013 Daniel Dietze
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

    Device driver configuration dialog for National Instruments PXI-5122 DAQ card
 
"""

# NI-PXI 5122 - Settings Dialog for TERA GUI
# 
# (c) 2010, D. Dietze
# new: 16.08.2012 added 

# wx for general GUI
import wx
from math import pi

class PXI5122config(wx.Dialog):
	# config is the configuration dictionary from the input device class for the PXI5122
	# no direct access to digitizer hardware!!
	# only control elements interesting for the specialized measurement mode for the
	# 1kHz amplified system are kept compared to the pxi5122_config file for the oscilloscope app.
	def __init__(self, config):
		wx.Dialog.__init__(self, None, -1, 'PXI5122 Configuration')		
		
		self.propertymap = {"vertical" : {"impedance" : [50, 1000000], 
			"frequency" : [-1, 0, 20000000, 35000000, 100000000], 
			"range" : [20.0, 10.0, 4.0, 2.0, 1.0, 0.4, 0.2], 
			"coupling" : [0, 1, 2] }, 
			"trigger" : {"source" : [-1, 0, 1, 2], 
			"slope" : [-1, 1],
			"coupling" : [0, 1, 2, 3, 1001],
			"reference" : [0.0, 33.33333, 66.66666, 100.0]},
			"timing" : {"clock" : [0, 1],
			"realtime" : [1, 0]},
			"measurement" : {"mode" : [0, 1], 
			"refmode" : [3, 5], 			
			"CH1mode" : [0, 1, 2, 3, 4]}
			}
		
		# add controls for
		# 'holdoff' -> internal waiting time, NOT trigger holdoff
		# 'refpos', 'records'
		# 'trig_level', 'trig_slope', 'trig_delay' 
		# 'ch0_impedance', 'ch0_range', 'ch0_offset'
		# 'ch1_impedance', 'ch1_range', 'ch1_offset'
		# 'averaging mode', 'integration time constant'
		self.channel0_impedance_label = wx.StaticText(self, -1, "Input Impedance")
		self.channel0_impedance = wx.Choice(self, -1, choices=["50Ohm", "1MOhm"])
		self.channel0_range_label = wx.StaticText(self, -1, "Input Range")
		self.channel0_range = wx.Choice(self, -1, choices=["20V", "10V", "4V", "2V", "1", "400mV", "200mV"])
		self.channel0_offset_label = wx.StaticText(self, -1, "Range Offset (V)")
		self.channel0_offset = wx.TextCtrl(self, -1, "0", style = wx.TE_RIGHT)
		self.holdoff_label = wx.StaticText(self, -1, "Wait (s)")
		self.holdoff = wx.TextCtrl(self, -1, "0.0")
		self.choice_refmode_label = wx.StaticText(self, -1, "Reference Mode")
		self.choice_refmode = wx.Choice(self, -1, choices=["Linear", "Cubic"])
		
		self.channel1_impedance_label = wx.StaticText(self, -1, "Input Impedance")
		self.channel1_impedance = wx.Choice(self, -1, choices=["50Ohm", "1MOhm"])
		self.channel1_range_label = wx.StaticText(self, -1, "Input Range")
		self.channel1_range = wx.Choice(self, -1, choices=["20V", "10V", "4V", "2V", "1V", "400mV", "200mV"])
		self.channel1_offset_label = wx.StaticText(self, -1, "Range Offset (V)")
		self.channel1_offset = wx.TextCtrl(self, -1, "0", style = wx.TE_RIGHT)		
		self.choice_CH1mode_label = wx.StaticText(self, -1, "CH1 Usage:")
		self.choice_CH1mode = wx.Choice(self, -1, choices=["Nothing", "CH0 Modulation", "CH0 Normalization", "Detection Gate", "A-B"])
		self.mod_level_label = wx.StaticText(self, -1, "Mod. Threshold (V)")
		self.mod_level = wx.TextCtrl(self, -1, "0.0")
		self.gatewidth_label = wx.StaticText(self, -1, "Gate width (sigma)")
		self.gatewidth = wx.TextCtrl(self, -1, "1.0")
		#self.gate_max_level_label = wx.StaticText(self, -1, "Gate max. (V)")
		#self.gate_max_level = wx.TextCtrl(self, -1, "0.0")				
		
		self.trigger_level_label = wx.StaticText(self, -1, "Level (V)")
		self.trigger_level = wx.TextCtrl(self, -1, "0.0")
		self.trigger_slope_label = wx.StaticText(self, -1, "Slope")
		self.trigger_slope = wx.Choice(self, -1, choices=["Neg.", "Pos."])
		self.trigger_delay_label = wx.StaticText(self, -1, "Delay (s)")
		self.trigger_delay = wx.TextCtrl(self, -1, "0.0")
		self.horizontal_records_label = wx.StaticText(self, -1, "Records / Sample")
		self.horizontal_records = wx.TextCtrl(self, -1, "1")
		self.horizontal_reference_label = wx.StaticText(self, -1, "Pre-to-Post-Ratio")
		self.horizontal_reference = wx.Choice(self, -1, choices=["0:3", "1:2", "2:1", "3:0"])
		self.avg_mode_label = wx.StaticText(self, -1, "Averaging Mode")
		self.avg_mode = wx.Choice(self, -1, choices=["Box", "Bessel"])
		self.avg_time_label = wx.StaticText(self, -1, "Int.time (ms)")
		self.avg_time = wx.TextCtrl(self, -1, "30.0")
		
		# dialog buttons
		self.cancel_button = wx.Button(self, wx.ID_CANCEL, "Cancel")		
		self.ok_button = wx.Button(self, wx.ID_OK, "Apply")
		
		# arrange objects and set layout
		self.__set_properties(config)
		self.__do_layout()
		
		# event bindings
		self.Bind(wx.EVT_CHOICE, self.onChannel0Impedance, self.channel0_impedance)
		self.Bind(wx.EVT_CHOICE, self.onChannel0Range, self.channel0_range)
		self.channel0_offset.Bind(wx.EVT_KILL_FOCUS, self.onChannel0Offset, self.channel0_offset)
		self.Bind(wx.EVT_CHOICE, self.onChannel1Impedance, self.channel1_impedance)
		self.Bind(wx.EVT_CHOICE, self.onChannel1Range, self.channel1_range)
		self.channel1_offset.Bind(wx.EVT_KILL_FOCUS, self.onChannel1Offset, self.channel1_offset)
		
		self.trigger_delay.Bind(wx.EVT_KILL_FOCUS, self.onTriggerDelay, self.trigger_delay)
		self.holdoff.Bind(wx.EVT_KILL_FOCUS, self.onHoldoff, self.holdoff)
		self.trigger_level.Bind(wx.EVT_KILL_FOCUS, self.onTriggerLevel, self.trigger_level)
		self.Bind(wx.EVT_CHOICE, self.onTriggerSlope, self.trigger_slope)
		self.horizontal_records.Bind(wx.EVT_KILL_FOCUS, self.onHorizontalRecords, self.horizontal_records)
		self.Bind(wx.EVT_CHOICE, self.onHorizontalReference, self.horizontal_reference)
		self.Bind(wx.EVT_CHOICE, self.onAvgMode, self.avg_mode)
		self.avg_time.Bind(wx.EVT_KILL_FOCUS, self.onAvgTime, self.avg_time)
		
		self.Bind(wx.EVT_CHOICE, self.onCH1Mode, self.choice_CH1mode)		
		#self.mod_level.Bind(wx.EVT_KILL_FOCUS, self.onModLevel, self.mod_level)
		#self.gate_min_level.Bind(wx.EVT_KILL_FOCUS, self.onGateMinLevel, self.gate_min_level)
		#self.gate_max_level.Bind(wx.EVT_KILL_FOCUS, self.onGateMaxLevel, self.gate_max_level)
		
	# set properties and layout
	def __set_properties(self, config):		
		# 'holdoff'
		# 'refpos', 'records'
		# 'trig_level', 'trig_slope', 'trig_delay' 
		# 'ch0_impedance', 'ch0_range', 'ch0_offset'
		# 'ch1_impedance', 'ch1_range', 'ch1_offset'
		self.channel0_impedance.SetSelection(self.propertymap['vertical']['impedance'].index(config['ch0_impedance']))
		self.channel0_range.SetSelection(self.propertymap['vertical']['range'].index(config['ch0_range']))
		self.channel0_offset.SetValue(str(config['ch0_offset']))
		self.channel1_impedance.SetSelection(self.propertymap['vertical']['impedance'].index(config['ch1_impedance']))
		self.channel1_range.SetSelection(self.propertymap['vertical']['range'].index(config['ch1_range']))
		self.channel1_offset.SetValue(str(config['ch1_offset']))
		self.choice_refmode.SetSelection(self.propertymap['measurement']['refmode'].index(config['refmode']))
		
		self.choice_CH1mode.SetSelection(self.propertymap['measurement']['CH1mode'].index(config['CH1mode']))
		
		self.trigger_level.SetValue(str(config['trig_level']))
		self.trigger_slope.SetSelection(self.propertymap['trigger']['slope'].index(config['trig_slope']))
		self.trigger_delay.SetValue(str(config['trig_delay']))
		
		self.holdoff.SetValue(str(config['holdoff']))
		self.horizontal_reference.SetSelection(self.propertymap['trigger']['reference'].index(config['refpos']))
		self.horizontal_records.SetValue(str(config['records']))
		
		self.avg_mode.SetSelection(self.propertymap['measurement']['mode'].index(config['intmode']))
		self.avg_time.SetValue(str(config['inttime']))
				
		self.mod_level.SetValue(str(config['modlevel']))
		self.gatewidth.SetValue(str(config['gatewidth']))
		#self.gate_max_level.SetValue(str(config['gatemaxlevel']))
		
		# check enabled state of all controls
		self.enableChannelOffsetControl(0)
		self.enableChannelOffsetControl(1)
		self.enableAvgTimeControl()
		self.enableCH1UsageControl()
		
	def __do_layout(self):
		main_sizer = wx.BoxSizer(wx.VERTICAL)
				
		# channels
		hbox2 = wx.BoxSizer(wx.HORIZONTAL)
		vbox1st = wx.StaticBox(self, -1, "Channel 0")
		vbox1 = wx.StaticBoxSizer(vbox1st, wx.VERTICAL)
		hbox1v1 = wx.BoxSizer(wx.HORIZONTAL)
		hbox1v1.Add(self.channel0_impedance_label, 1, wx.ALL | wx.EXPAND, 2)
		hbox1v1.Add(self.channel0_impedance, 1, wx.ALL | wx.EXPAND, 2)
		vbox1.Add(hbox1v1, 0, wx.EXPAND)
		hbox4v1 = wx.BoxSizer(wx.HORIZONTAL)
		hbox4v1.Add(self.channel0_range_label, 1, wx.ALL | wx.EXPAND, 2)
		hbox4v1.Add(self.channel0_range, 1, wx.ALL | wx.EXPAND, 2)
		vbox1.Add(hbox4v1, 0, wx.EXPAND)
		hbox5v1 = wx.BoxSizer(wx.HORIZONTAL)
		hbox5v1.Add(self.channel0_offset_label, 1, wx.ALL | wx.EXPAND, 2)
		hbox5v1.Add(self.channel0_offset, 1, wx.ALL | wx.EXPAND, 2)
		vbox1.Add(hbox5v1, 0, wx.EXPAND)		
		hbox5v3 = wx.BoxSizer(wx.HORIZONTAL)
		hbox5v3.Add(self.holdoff_label, 1, wx.ALL | wx.EXPAND, 2)
		hbox5v3.Add(self.holdoff, 1, wx.ALL | wx.EXPAND, 2)
		vbox1.Add(hbox5v3, 0, wx.EXPAND)
		hbox6v2 = wx.BoxSizer(wx.HORIZONTAL)
		hbox6v2.Add(self.choice_refmode_label, 1, wx.ALL | wx.EXPAND, 2)
		hbox6v2.Add(self.choice_refmode, 1, wx.ALL | wx.EXPAND, 2)
		vbox1.Add(hbox6v2, 0, wx.EXPAND)
		hbox2.Add(vbox1, 0, wx.EXPAND)
		
		vbox2st = wx.StaticBox(self, -1, "Channel 1")
		vbox2 = wx.StaticBoxSizer(vbox2st, wx.VERTICAL)
		hbox1v2 = wx.BoxSizer(wx.HORIZONTAL)
		hbox1v2.Add(self.channel1_impedance_label, 1, wx.ALL | wx.EXPAND, 2)
		hbox1v2.Add(self.channel1_impedance, 1, wx.ALL | wx.EXPAND, 2)
		vbox2.Add(hbox1v2, 0, wx.EXPAND)
		hbox4v2 = wx.BoxSizer(wx.HORIZONTAL)
		hbox4v2.Add(self.channel1_range_label, 1, wx.ALL | wx.EXPAND, 2)
		hbox4v2.Add(self.channel1_range, 1, wx.ALL | wx.EXPAND, 2)
		vbox2.Add(hbox4v2, 0, wx.EXPAND)
		hbox5v2 = wx.BoxSizer(wx.HORIZONTAL)
		hbox5v2.Add(self.channel1_offset_label, 1, wx.ALL | wx.EXPAND, 2)
		hbox5v2.Add(self.channel1_offset, 1, wx.ALL | wx.EXPAND, 2)
		vbox2.Add(hbox5v2, 0, wx.EXPAND)
		hbox6v2b = wx.BoxSizer(wx.HORIZONTAL)
		hbox6v2b.Add(self.choice_CH1mode_label, 1, wx.ALL | wx.EXPAND, 2)
		hbox6v2b.Add(self.choice_CH1mode, 1, wx.ALL | wx.EXPAND, 2)
		vbox2.Add(hbox6v2b, 0, wx.EXPAND)
		hbox7v2 = wx.BoxSizer(wx.HORIZONTAL)
		hbox7v2.Add(self.mod_level_label, 1, wx.ALL | wx.EXPAND, 2)
		hbox7v2.Add(self.mod_level, 1, wx.ALL | wx.EXPAND, 2)
		vbox2.Add(hbox7v2, 0, wx.EXPAND)
		hbox8v2b = wx.BoxSizer(wx.HORIZONTAL)
		hbox8v2b.Add(self.gatewidth_label, 1, wx.ALL | wx.EXPAND, 2)
		hbox8v2b.Add(self.gatewidth, 1, wx.ALL | wx.EXPAND, 2)
		vbox2.Add(hbox8v2b, 0, wx.EXPAND)
		#hbox8v2 = wx.BoxSizer(wx.HORIZONTAL)
		#hbox8v2.Add(self.gate_min_level_label, 1, wx.ALL | wx.EXPAND, 2)
		#hbox8v2.Add(self.gate_min_level, 1, wx.ALL | wx.EXPAND, 2)
		#vbox2.Add(hbox8v2, 0, wx.EXPAND)
		#hbox9v2 = wx.BoxSizer(wx.HORIZONTAL)
		#hbox9v2.Add(self.gate_max_level_label, 1, wx.ALL | wx.EXPAND, 2)
		#hbox9v2.Add(self.gate_max_level, 1, wx.ALL | wx.EXPAND, 2)
		#vbox2.Add(hbox9v2, 0, wx.EXPAND)
		hbox2.Add(vbox2, 0, wx.EXPAND)
		
		vbox3st = wx.StaticBox(self, -1, "Timing")
		vbox3 = wx.StaticBoxSizer(vbox3st, wx.VERTICAL)
		hbox2v3 = wx.BoxSizer(wx.HORIZONTAL)
		hbox2v3.Add(self.trigger_level_label, 1, wx.ALL | wx.EXPAND, 2)
		hbox2v3.Add(self.trigger_level, 1, wx.ALL | wx.EXPAND, 2)
		vbox3.Add(hbox2v3, 0, wx.EXPAND)
		hbox3v3 = wx.BoxSizer(wx.HORIZONTAL)
		hbox3v3.Add(self.trigger_slope_label, 1, wx.ALL | wx.EXPAND, 2)
		hbox3v3.Add(self.trigger_slope, 1, wx.ALL | wx.EXPAND, 2)
		vbox3.Add(hbox3v3, 0, wx.EXPAND)
		hbox4v3 = wx.BoxSizer(wx.HORIZONTAL)
		hbox4v3.Add(self.trigger_delay_label, 1, wx.ALL | wx.EXPAND, 2)
		hbox4v3.Add(self.trigger_delay, 1, wx.ALL | wx.EXPAND, 2)
		vbox3.Add(hbox4v3, 0, wx.EXPAND)
		hbox5v3 = wx.BoxSizer(wx.HORIZONTAL)
		hbox5v3.Add(self.horizontal_records_label, 1, wx.ALL | wx.EXPAND, 2)
		hbox5v3.Add(self.horizontal_records, 1, wx.ALL | wx.EXPAND, 2)
		vbox3.Add(hbox5v3, 0, wx.EXPAND)
		hbox6v3 = wx.BoxSizer(wx.HORIZONTAL)
		hbox6v3.Add(self.horizontal_reference_label, 1, wx.ALL | wx.EXPAND, 2)
		hbox6v3.Add(self.horizontal_reference, 1, wx.ALL | wx.EXPAND, 2)
		vbox3.Add(hbox6v3, 0, wx.EXPAND)				
		hbox7v3 = wx.BoxSizer(wx.HORIZONTAL)
		hbox7v3.Add(self.avg_mode_label, 1, wx.ALL | wx.EXPAND, 2)
		hbox7v3.Add(self.avg_mode, 1, wx.ALL | wx.EXPAND, 2)
		vbox3.Add(hbox7v3, 0, wx.EXPAND)	
		hbox8v3 = wx.BoxSizer(wx.HORIZONTAL)
		hbox8v3.Add(self.avg_time_label, 1, wx.ALL | wx.EXPAND, 2)
		hbox8v3.Add(self.avg_time, 1, wx.ALL | wx.EXPAND, 2)
		vbox3.Add(hbox8v3, 0, wx.EXPAND)
		hbox2.Add(vbox3, 0, wx.EXPAND)	
		
		main_sizer.Add(hbox2, 0, wx.ALL | wx.EXPAND, 2)
		
		# dialog buttons
		buttonSizer = wx.BoxSizer(wx.HORIZONTAL)						
		buttonSizer.Add(self.cancel_button, 0, wx.ALL | wx.ALIGN_CENTER, 2)		
		buttonSizer.Add(self.ok_button, 0, wx.ALL | wx.ALIGN_CENTER, 2)				
		main_sizer.Add(buttonSizer, 0, wx.ALL | wx.ALIGN_CENTER, 2)
		
		# attach main sizer to panel to adjust element sizes
		self.SetAutoLayout(True)
		self.SetSizer(main_sizer)
		self.Fit()		
	
	def enableAvgTimeControl(self):
		if(self.avg_mode.GetSelection() == 0):
			self.avg_time.Enable(False)
		else:
			self.avg_time.Enable(True)
			
	def enableCH1UsageControl(self):
		if(self.choice_CH1mode.GetSelection() == 0 or self.choice_CH1mode.GetSelection() == 2):
			self.mod_level.Enable(False)
			#self.gate_min_level.Enable(False)
			#self.gate_max_level.Enable(False)
			self.gatewidth.Enable(False)
		elif(self.choice_CH1mode.GetSelection() == 1):
			self.mod_level.Enable(True)
			#self.gate_min_level.Enable(False)
			#self.gate_max_level.Enable(False)
			self.gatewidth.Enable(False)
		else:
			self.mod_level.Enable(False)
			#self.gate_min_level.Enable(True)
			#self.gate_max_level.Enable(True)
			self.gatewidth.Enable(True)
	
	def enableChannelOffsetControl(self, id):
		if(id == 0):
			if(self.channel0_impedance.GetSelection() == 0 and self.channel0_range.GetSelection() <= 1):
				self.channel0_offset.SetValue("0")
				self.channel0_offset.Enable(False)
			elif(self.channel0_impedance.GetSelection() == 1 and self.channel0_range.GetSelection() == 0):
				self.channel0_offset.SetValue("0")
				self.channel0_offset.Enable(False)
			else:
				self.channel0_offset.Enable(self.channel0_range.IsEnabled())	# couple the offset control to the range control			
		else:
			if(self.channel1_impedance.GetSelection() == 0 and self.channel1_range.GetSelection() <= 1):
				self.channel1_offset.SetValue("0")
				self.channel1_offset.Enable(False)
			elif(self.channel1_impedance.GetSelection() == 1 and self.channel1_range.GetSelection() == 0):
				self.channel1_offset.SetValue("0")
				self.channel1_offset.Enable(False)
			else:
				self.channel1_offset.Enable(self.channel1_range.IsEnabled())	# couple the offset control to the range control
			
	def onChannel0Impedance(self, event):
		# 50 Ohms is incompatible with 20V range
		if self.channel0_impedance.GetSelection() == 0 and self.channel0_range.GetSelection() == 0:
			self.channel0_range.SetSelection(1)
		# check offset
		self.enableChannelOffsetControl(0)
		
	def onChannel0Range(self, event):
		# 50 Ohms is incompatible with 20V range
		if self.channel0_impedance.GetSelection() == 0 and self.channel0_range.GetSelection() == 0:
			self.channel0_range.SetSelection(1)
		if self.channel0_impedance.GetSelection() == 0 and self.channel0_range.GetSelection() <= 1:
			self.channel0_offset.SetValue("0")		
		# check offset
		self.enableChannelOffsetControl(0)
		
	def onChannel0Offset(self, event):
		# offset has to be in the range -range/2 .. range/2		
		offset = float(self.channel0_offset.GetValue())
		range = self.propertymap["vertical"]["range"][self.channel0_range.GetSelection()]
		if(offset < -range/2):
			offset = -range/2
			self.channel0_offset.SetValue(str(offset))
		if(offset > range/2):
			offset = range/2
			self.channel0_offset.SetValue(str(offset))
		
	def onChannel1Impedance(self, event):
		# 50 Ohms is incompatible with 20V range
		if self.channel1_impedance.GetSelection() == 0 and self.channel1_range.GetSelection() == 0:
			self.channel1_range.SetSelection(1)
		# check offset
		self.enableChannelOffsetControl(1)
		
	def onChannel1Range(self, event):
		# 50 Ohms is incompatible with 20V range
		if self.channel1_impedance.GetSelection() == 0 and self.channel1_range.GetSelection() == 0:
			self.channel1_range.SetSelection(1)
		if self.channel1_impedance.GetSelection() == 0 and self.channel1_range.GetSelection() <= 1:
			self.channel1_offset.SetValue("0")
		# check offset
		self.enableChannelOffsetControl(1)	
				
	def onChannel1Offset(self, event):		
		# offset has to be in the range -range/2 .. range/2
		offset = float(self.channel1_offset.GetValue())
		range = self.propertymap["vertical"]["range"][self.channel1_range.GetSelection()]
		if(offset < -range/2):
			offset = -range/2
			self.channel1_offset.SetValue(str(offset))
		if(offset > range/2):
			offset = range/2
			self.channel1_offset.SetValue(str(offset))		
				
	def onTriggerLevel(self, event):		
		pos_limit = 5.0				# limits of EXT. TRIG.
		neg_limit = -5.0
		if(float(self.trigger_level.GetValue()) < neg_limit):
			self.trigger_level.SetValue(str(neg_limit))
		if(float(self.trigger_level.GetValue()) > pos_limit):
			self.trigger_level.SetValue(str(pos_limit))
		
	def onTriggerSlope(self, event):
		pass
	
	def onTriggerDelay(self, event):
		if(float(self.trigger_delay.GetValue()) < 0.0):
			self.trigger_delay.SetValue("0.0")
	
	def onHoldoff(self, event):
		if(float(self.holdoff.GetValue()) < 0.0):
			self.holdoff.SetValue("0.0")
				
	def onHorizontalRecords(self, event):
		if float(self.horizontal_records.GetValue()) < 1:
			self.horizontal_records.SetValue("1")
		elif float(self.horizontal_records.GetValue()) > 100000:
			self.horizontal_records.SetValue("100000")
				
	def onHorizontalReference(self, event):
		pass
	
	def onAvgMode(self, event):
		self.enableAvgTimeControl()
	
	def onAvgTime(self, event):
		if(float(self.avg_time.GetValue()) < 1):
			self.avg_time.SetValue("1.0")
		elif(float(self.avg_time.GetValue()) > float(self.horizontal_records.GetValue())):
			self.avg_time.SetValue(self.horizontal_records.GetValue())
	
	def onCH1Mode(self, event):
		self.enableCH1UsageControl()
		
	def get_configuration(self):
		config = {}
		config['records'] = int(self.horizontal_records.GetValue())
		config['ch0_offset'] = float(self.channel0_offset.GetValue())
		config['ch1_offset'] = float(self.channel1_offset.GetValue())
		config['trig_level'] = float(self.trigger_level.GetValue())
		config['trig_delay'] = float(self.trigger_delay.GetValue())
		config['holdoff'] = float(self.holdoff.GetValue())
		config['inttime'] = float(self.avg_time.GetValue())
		
		config['ch0_impedance'] = self.propertymap['vertical']['impedance'][self.channel0_impedance.GetSelection()]
		config['ch1_impedance'] = self.propertymap['vertical']['impedance'][self.channel1_impedance.GetSelection()]
		config['ch0_range'] = self.propertymap['vertical']['range'][self.channel0_range.GetSelection()]
		config['ch1_range'] = self.propertymap['vertical']['range'][self.channel1_range.GetSelection()]
		config['trig_slope'] = self.propertymap['trigger']['slope'][self.trigger_slope.GetSelection()]
		config['refpos'] = self.propertymap['trigger']['reference'][self.horizontal_reference.GetSelection()]
		config['intmode'] = self.propertymap['measurement']['mode'][self.avg_mode.GetSelection()]
		config['refmode'] = self.propertymap['measurement']['refmode'][self.choice_refmode.GetSelection()]
		
		config['CH1mode'] = self.propertymap['measurement']['CH1mode'][self.choice_CH1mode.GetSelection()]
		config['modlevel'] = float(self.mod_level.GetValue())
		config['gatewidth'] = float(self.gatewidth.GetValue())
		#config['gatemaxlevel'] = float(self.gate_max_level.GetValue())
		
		return config

		
# ##############################################################################################################
# same for lock-in mode
class PXI5122LockInConfig(wx.Dialog):
	# config is the configuration dictionary from the input device class for the PXI5122LockIn
	# no direct access to digitizer hardware!!
	def __init__(self, config):
		wx.Dialog.__init__(self, None, -1, 'PXI5122LockIn Configuration')		

		self.propertymap = {"vertical" : {"impedance" : [50, 1000000], 
			"filter" : [-1, 0, 20000000, 35000000, 100000000], 
			"frequency" : [-1, 0, 20000000, 35000000, 100000000], 
			"range" : [20.0, 10.0, 4.0, 2.0, 1.0, 0.4, 0.2], 
			"coupling" : [0, 1, 2] }, 
			"trigger" : {"source" : [-1, 0, 1, 2], 
			"slope" : [-1, 1],
			"coupling" : [0, 1, 2, 3, 1001],
			"reference" : [0.0, 33.33333, 66.66666, 100.0]},
			"timing" : {"clock" : [0, 1],
			"realtime" : [1, 0]},
			"measurement" : {"signal" : [0, 1, 2, 3]}
			}
		
		# add controls for
		# 'holdoff' -> internal waiting time, NOT trigger holdoff
		# 'refpos', 'records'
		# 'trig_level', 'trig_slope', 'trig_delay' 
		# 'ch0_impedance', 'ch0_range', 'ch0_offset'
		# 'ch1_impedance', 'ch1_range', 'ch1_offset'
		# 'averaging mode', 'integration time constant'
		self.channel0_impedance_label = wx.StaticText(self, -1, "Input Impedance")
		self.channel0_impedance = wx.Choice(self, -1, choices=["50Ohm", "1MOhm"])
		self.channel0_filter_label = wx.StaticText(self, -1, "Input Filter")
		self.channel0_filter = wx.Choice(self, -1, choices=["None", "Default", "20MHz", "35MHz", "100MHz"])
		self.channel0_range_label = wx.StaticText(self, -1, "Input Range")
		self.channel0_range = wx.Choice(self, -1, choices=["20V", "10V", "4V", "2V", "1V", "400mV", "200mV"])
		self.channel0_offset_label = wx.StaticText(self, -1, "Range Offset (V)")
		self.channel0_offset = wx.TextCtrl(self, -1, "0", style = wx.TE_RIGHT)
		
		self.channel1_impedance_label = wx.StaticText(self, -1, "Input Impedance")
		self.channel1_impedance = wx.Choice(self, -1, choices=["50Ohm", "1MOhm"])
		self.channel1_filter_label = wx.StaticText(self, -1, "Input Filter")
		self.channel1_filter = wx.Choice(self, -1, choices=["None", "Default", "20MHz", "35MHz", "100MHz"])
		self.channel1_range_label = wx.StaticText(self, -1, "Input Range")
		self.channel1_range = wx.Choice(self, -1, choices=["20V", "10V", "4V", "2V", "1V", "400mV", "200mV"])
		self.channel1_offset_label = wx.StaticText(self, -1, "Range Offset (V)")
		self.channel1_offset = wx.TextCtrl(self, -1, "0", style = wx.TE_RIGHT)		
		
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
		self.__set_properties(config)
		self.__do_layout()
		
		# event bindings
		self.Bind(wx.EVT_CHOICE, self.onChannel0Impedance, self.channel0_impedance)
		self.Bind(wx.EVT_CHOICE, self.onChannel0Range, self.channel0_range)
		#self.Bind(wx.EVT_CHOICE, self.onChannel0Filter, self.channel0_filter)
		self.channel0_offset.Bind(wx.EVT_KILL_FOCUS, self.onChannel0Offset, self.channel0_offset)
		self.Bind(wx.EVT_CHOICE, self.onChannel1Impedance, self.channel1_impedance)
		self.Bind(wx.EVT_CHOICE, self.onChannel1Range, self.channel1_range)
		#self.Bind(wx.EVT_CHOICE, self.onChannel1Filter, self.channel1_filter)
		self.channel1_offset.Bind(wx.EVT_KILL_FOCUS, self.onChannel1Offset, self.channel1_offset)
		
		self.holdoff.Bind(wx.EVT_KILL_FOCUS, self.onHoldoff, self.holdoff)
		self.avg_time.Bind(wx.EVT_KILL_FOCUS, self.onAvgTime, self.avg_time)
		self.phase.Bind(wx.EVT_KILL_FOCUS, self.onPhase, self.phase)
		#self.Bind(wx.EVT_CHOICE, self.onSignal, self.signal)
		
	# set properties and layout
	def __set_properties(self, config):		
		# 'holdoff'
		# 'refpos', 'records'
		# 'trig_level', 'trig_slope', 'trig_delay' 
		# 'ch0_impedance', 'ch0_range', 'ch0_offset'
		# 'ch1_impedance', 'ch1_range', 'ch1_offset'
		self.channel0_impedance.SetSelection(self.propertymap['vertical']['impedance'].index(config['ch0_impedance']))
		self.channel0_range.SetSelection(self.propertymap['vertical']['range'].index(config['ch0_range']))
		self.channel0_filter.SetSelection(self.propertymap['vertical']['filter'].index(config['ch0_filter']))
		self.channel0_offset.SetValue(str(config['ch0_offset']))
		self.channel1_impedance.SetSelection(self.propertymap['vertical']['impedance'].index(config['ch1_impedance']))
		self.channel1_range.SetSelection(self.propertymap['vertical']['range'].index(config['ch1_range']))
		self.channel1_filter.SetSelection(self.propertymap['vertical']['filter'].index(config['ch1_filter']))
		self.channel1_offset.SetValue(str(config['ch1_offset']))
			
		self.holdoff.SetValue(str(config['holdoff']))
		self.avg_time.SetValue(str(config['inttime']))
		self.phase.SetValue(str(config['PHI'] * 180.0 / pi))
		self.signal.SetSelection(self.propertymap['measurement']['signal'].index(config['signal']))		
		
		self.autophase.SetValue(False)
		
		# check enabled state of all controls
		self.enableChannelOffsetControl(0)
		self.enableChannelOffsetControl(1)
		
	def __do_layout(self):
		main_sizer = wx.BoxSizer(wx.VERTICAL)
				
		# channels
		hbox2 = wx.BoxSizer(wx.HORIZONTAL)
		vbox1st = wx.StaticBox(self, -1, "Channel 0")
		vbox1 = wx.StaticBoxSizer(vbox1st, wx.VERTICAL)
		hbox1v1 = wx.BoxSizer(wx.HORIZONTAL)
		hbox1v1.Add(self.channel0_impedance_label, 1, wx.ALL | wx.EXPAND, 2)
		hbox1v1.Add(self.channel0_impedance, 1, wx.ALL | wx.EXPAND, 2)
		vbox1.Add(hbox1v1, 0, wx.EXPAND)
		hbox6v2 = wx.BoxSizer(wx.HORIZONTAL)
		hbox6v2.Add(self.channel0_filter_label, 1, wx.ALL | wx.EXPAND, 2)
		hbox6v2.Add(self.channel0_filter, 1, wx.ALL | wx.EXPAND, 2)
		vbox1.Add(hbox6v2, 0, wx.EXPAND)
		hbox4v1 = wx.BoxSizer(wx.HORIZONTAL)
		hbox4v1.Add(self.channel0_range_label, 1, wx.ALL | wx.EXPAND, 2)
		hbox4v1.Add(self.channel0_range, 1, wx.ALL | wx.EXPAND, 2)
		vbox1.Add(hbox4v1, 0, wx.EXPAND)
		hbox5v1 = wx.BoxSizer(wx.HORIZONTAL)
		hbox5v1.Add(self.channel0_offset_label, 1, wx.ALL | wx.EXPAND, 2)
		hbox5v1.Add(self.channel0_offset, 1, wx.ALL | wx.EXPAND, 2)
		vbox1.Add(hbox5v1, 0, wx.EXPAND)		
		hbox2.Add(vbox1, 0, wx.EXPAND)
		
		vbox2st = wx.StaticBox(self, -1, "Channel 1")
		vbox2 = wx.StaticBoxSizer(vbox2st, wx.VERTICAL)
		hbox1v2 = wx.BoxSizer(wx.HORIZONTAL)
		hbox1v2.Add(self.channel1_impedance_label, 1, wx.ALL | wx.EXPAND, 2)
		hbox1v2.Add(self.channel1_impedance, 1, wx.ALL | wx.EXPAND, 2)
		vbox2.Add(hbox1v2, 0, wx.EXPAND)
		hbox3v2 = wx.BoxSizer(wx.HORIZONTAL)
		hbox3v2.Add(self.channel1_filter_label, 1, wx.ALL | wx.EXPAND, 2)
		hbox3v2.Add(self.channel1_filter, 1, wx.ALL | wx.EXPAND, 2)
		vbox2.Add(hbox3v2, 0, wx.EXPAND)
		hbox4v2 = wx.BoxSizer(wx.HORIZONTAL)
		hbox4v2.Add(self.channel1_range_label, 1, wx.ALL | wx.EXPAND, 2)
		hbox4v2.Add(self.channel1_range, 1, wx.ALL | wx.EXPAND, 2)
		vbox2.Add(hbox4v2, 0, wx.EXPAND)
		hbox5v2 = wx.BoxSizer(wx.HORIZONTAL)
		hbox5v2.Add(self.channel1_offset_label, 1, wx.ALL | wx.EXPAND, 2)
		hbox5v2.Add(self.channel1_offset, 1, wx.ALL | wx.EXPAND, 2)
		vbox2.Add(hbox5v2, 0, wx.EXPAND)
		hbox2.Add(vbox2, 0, wx.EXPAND)
		
		vbox3st = wx.StaticBox(self, -1, "Lcok-In Parameters")
		vbox3 = wx.StaticBoxSizer(vbox3st, wx.VERTICAL)
		hbox5v3 = wx.BoxSizer(wx.HORIZONTAL)
		hbox5v3.Add(self.holdoff_label, 1, wx.ALL | wx.EXPAND, 2)
		hbox5v3.Add(self.holdoff, 1, wx.ALL | wx.EXPAND, 2)
		vbox3.Add(hbox5v3, 0, wx.EXPAND)
		hbox8v3 = wx.BoxSizer(wx.HORIZONTAL)
		hbox8v3.Add(self.avg_time_label, 1, wx.ALL | wx.EXPAND, 2)
		hbox8v3.Add(self.avg_time, 1, wx.ALL | wx.EXPAND, 2)
		vbox3.Add(hbox8v3, 0, wx.EXPAND)
		hbox3v3 = wx.BoxSizer(wx.HORIZONTAL)
		hbox3v3.Add(self.phase_label, 1, wx.ALL | wx.EXPAND, 2)
		hbox3v3.Add(self.phase, 1, wx.ALL | wx.EXPAND, 2)
		vbox3.Add(hbox3v3, 0, wx.EXPAND)
		hbox2v3 = wx.BoxSizer(wx.HORIZONTAL)
		hbox2v3.Add(self.signal_label, 1, wx.ALL | wx.EXPAND, 2)
		hbox2v3.Add(self.signal, 1, wx.ALL | wx.EXPAND, 2)
		vbox3.Add(hbox2v3, 0, wx.EXPAND)
		hbox4v3 = wx.BoxSizer(wx.HORIZONTAL)
		hbox4v3.Add(self.autophase, 1, wx.ALL | wx.EXPAND, 2)
		vbox3.Add(hbox4v3, 0, wx.EXPAND)
		hbox2.Add(vbox3, 0, wx.EXPAND)	
		
		main_sizer.Add(hbox2, 0, wx.ALL | wx.EXPAND, 2)
		
		# dialog buttons
		buttonSizer = wx.BoxSizer(wx.HORIZONTAL)						
		buttonSizer.Add(self.cancel_button, 0, wx.ALL | wx.ALIGN_CENTER, 2)		
		buttonSizer.Add(self.ok_button, 0, wx.ALL | wx.ALIGN_CENTER, 2)				
		main_sizer.Add(buttonSizer, 0, wx.ALL | wx.ALIGN_CENTER, 2)
		
		# attach main sizer to panel to adjust element sizes
		self.SetAutoLayout(True)
		self.SetSizer(main_sizer)
		self.Fit()		
	
	def enableChannelOffsetControl(self, id):
		if(id == 0):
			if(self.channel0_impedance.GetSelection() == 0 and self.channel0_range.GetSelection() <= 1):
				self.channel0_offset.SetValue("0")
				self.channel0_offset.Enable(False)
			elif(self.channel0_impedance.GetSelection() == 1 and self.channel0_range.GetSelection() == 0):
				self.channel0_offset.SetValue("0")
				self.channel0_offset.Enable(False)
			else:
				self.channel0_offset.Enable(self.channel0_range.IsEnabled())	# couple the offset control to the range control			
		else:
			if(self.channel1_impedance.GetSelection() == 0 and self.channel1_range.GetSelection() <= 1):
				self.channel1_offset.SetValue("0")
				self.channel1_offset.Enable(False)
			elif(self.channel1_impedance.GetSelection() == 1 and self.channel1_range.GetSelection() == 0):
				self.channel1_offset.SetValue("0")
				self.channel1_offset.Enable(False)
			else:
				self.channel1_offset.Enable(self.channel1_range.IsEnabled())	# couple the offset control to the range control
			
	def onChannel0Impedance(self, event):
		# 50 Ohms is incompatible with 20V range
		if self.channel0_impedance.GetSelection() == 0 and self.channel0_range.GetSelection() == 0:
			self.channel0_range.SetSelection(1)
		# check offset
		self.enableChannelOffsetControl(0)
		
	def onChannel0Range(self, event):
		# 50 Ohms is incompatible with 20V range
		if self.channel0_impedance.GetSelection() == 0 and self.channel0_range.GetSelection() == 0:
			self.channel0_range.SetSelection(1)
		if self.channel0_impedance.GetSelection() == 0 and self.channel0_range.GetSelection() <= 1:
			self.channel0_offset.SetValue("0")		
		# check offset
		self.enableChannelOffsetControl(0)
		
	def onChannel0Offset(self, event):
		# offset has to be in the range -range/2 .. range/2		
		offset = float(self.channel0_offset.GetValue())
		range = self.propertymap["vertical"]["range"][self.channel0_range.GetSelection()]
		if(offset < -range/2):
			offset = -range/2
			self.channel0_offset.SetValue(str(offset))
		if(offset > range/2):
			offset = range/2
			self.channel0_offset.SetValue(str(offset))
			
	def onChannel1Impedance(self, event):
		# 50 Ohms is incompatible with 20V range
		if self.channel1_impedance.GetSelection() == 0 and self.channel1_range.GetSelection() == 0:
			self.channel1_range.SetSelection(1)
		# check offset
		self.enableChannelOffsetControl(1)
		
	def onChannel1Range(self, event):
		# 50 Ohms is incompatible with 20V range
		if self.channel1_impedance.GetSelection() == 0 and self.channel1_range.GetSelection() == 0:
			self.channel1_range.SetSelection(1)
		if self.channel1_impedance.GetSelection() == 0 and self.channel1_range.GetSelection() <= 1:
			self.channel1_offset.SetValue("0")
		# check offset
		self.enableChannelOffsetControl(1)	
				
	def onChannel1Offset(self, event):		
		# offset has to be in the range -range/2 .. range/2
		offset = float(self.channel1_offset.GetValue())
		range = self.propertymap["vertical"]["range"][self.channel1_range.GetSelection()]
		if(offset < -range/2):
			offset = -range/2
			self.channel1_offset.SetValue(str(offset))
		if(offset > range/2):
			offset = range/2
			self.channel1_offset.SetValue(str(offset))		
	
	def onHoldoff(self, event):
		if(float(self.holdoff.GetValue()) < 0.0):
			self.holdoff.SetValue("0.0")
					
	def onAvgTime(self, event):
		if(float(self.avg_time.GetValue()) < 1):
			self.avg_time.SetValue("1.0")
	
	def onPhase(self, event):
		self.phase.SetValue(str(float(self.phase.GetValue()) % 180.0))
		
	def get_configuration(self):
		config = {}
		
		config['ch0_offset'] = float(self.channel0_offset.GetValue())
		config['ch1_offset'] = float(self.channel1_offset.GetValue())
		config['PHI'] = float(self.phase.GetValue()) * pi / 180.0
		config['holdoff'] = float(self.holdoff.GetValue())
		config['inttime'] = float(self.avg_time.GetValue())
		
		config['ch0_impedance'] = self.propertymap['vertical']['impedance'][self.channel0_impedance.GetSelection()]
		config['ch1_impedance'] = self.propertymap['vertical']['impedance'][self.channel1_impedance.GetSelection()]
		config['ch0_range'] = self.propertymap['vertical']['range'][self.channel0_range.GetSelection()]
		config['ch1_range'] = self.propertymap['vertical']['range'][self.channel1_range.GetSelection()]
		config['ch0_filter'] = self.propertymap['vertical']['filter'][self.channel0_filter.GetSelection()]
		config['ch1_filter'] = self.propertymap['vertical']['filter'][self.channel1_filter.GetSelection()]
		config['signal'] = self.propertymap['measurement']['signal'][self.signal.GetSelection()]
		
		return config
