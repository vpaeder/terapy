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

    Device driver for ADwin data acquisition hardware
 
"""

from terapy.hardware.input.base import InputDevice, InputWidget, AntennaWidget
from time import sleep
import numpy as np
import wx

try:
    import adwin
    _support_ADWIN = True
except:
    _support_ADWIN = False
ADBoot = "C:\\adwin\\adwin9.btl"            # boot file for T9 processor - ADWin Box Gold
ADDev = 0x150                                # default device number

if _support_ADWIN == True:
    from ADwin_config import ADWinLockInConfig
    class ADWinLockIn(InputDevice):
        """
        
            Device driver for ADwin data acquisition hardware
         
        """
        def __init__(self):
            InputDevice.__init__(self)
            self.config = ['signal', 'PHI', 'holdoff', 'amplification', 'inttime', 'mode', 'reftrigger', 'CH1_f', 'CH1_A', 'CH2_f', 'CH2_A', 'flock']
            self.signal = 0
            self.PHI = 0.0
            self.holdoff = 0.0
            self.amplification = 0
            self.inttime = 300.0
            self.mode = 0
            self.reftrigger = 2.0
            self.CH1_f = 10000.0
            self.CH1_A = 0.01
            self.CH2_f = 3000.0
            self.CH2_A = 4.0
            self.flock = 0
            self.units = ["V", "V", "V", "deg", "Hz"]
            self.qtynames = ["X","Y","R","Phi","f"]
            
            self.fdet = 0.0    # detected frequency in Hz
            self.phi = 0.0  # last detected phase in rad
            
            # config files and ADWin binaries
            self.LIA_EXT = "lock_in_ext.T91"
            self.LIA_INT = "lock_in_int.T92"    
            
            self.AD = adwin.adwin()
            self.booted = False
        
        def initialize(self):
            # establish connection to ADWin box
            self.AD.stop_process(0)        # stop all processes
            self.AD.free_process(0)        # remove all processes from memory
            
            self.booted = False
            if self.AD.boot(ADDev, ADBoot) != 1:
                print "ADWinLockIn ERROR: No connection to ADWin Box !"
                print self.AD.get_last_error_text()            
                raise
            
            # load both processes
            self.AD.load_process(self.LIA_EXT)    # compiled as process 1
            self.AD.load_process(self.LIA_INT)    # compiled as process 2
            
            self.booted = True
            
            # send parameters and start processes
            self.send_configuration()
        
        def send_configuration(self):
            if(self.booted == False):
                return

            # stop all processes 
            self.AD.stop_process(0)
            
            # initialize the input parameters:
            # PAR_1:         amplification factor, 0 = +-10V, 1 = +- 5V, 2 = +-2.5V, 3 = +-1.25V
            self.AD.set_par(1, self.amplification)
            # PAR_2:         lock to which frequency (0: CH1, 1: CH2, 2: CH1-CH2, 3: CH1+CH2)
            self.AD.set_par(2, self.flock)
            # FPAR_6:        reference trigger threshold (V) (2V for TTL)
            self.AD.set_fpar(6, self.reftrigger)
            # FPAR_7:        lock-in time constant (s)
            self.AD.set_fpar(7, self.inttime/1000.0)
            # FPAR_8:        CH1 frequency (Hz)
            self.AD.set_fpar(8, self.CH1_f)
            # FPAR_9:        CH1 amplitude (V)
            #    self.AD.set_fpar(9, self.CH1_A)                # new: initialize always with zero amplitude
            self.AD.set_fpar(9, 0.0)                        
            # FPAR_10:        CH2 frequency
            self.AD.set_fpar(10, self.CH2_f)
            # FPAR_11:         CH2 amplitude
            self.AD.set_fpar(11, self.CH2_A)
                    
            # start the appropriate process
            if self.mode == 0:    # boot the LIA in external mode
                self.AD.start_process(1)
            else:
                self.AD.start_process(2)
            
            if self.AD.get_last_error() != 0:
                print "ADWinLockIn ERROR: Could not start process !"
                print self.AD.get_last_error_text()            
                raise            
        
        def set_amplitude(self, amplitude):
            if self.booted == False:
                return
            if amplitude < -10.0:
                amplitude = -10.0
            if amplitude > 10.0:
                amplitude = 10.0
            self.AD.set_fpar(9, amplitude)
            #self.AD.stop_process(0)
            #if self.mode == 0:    # boot the LIA in external mode
            #    self.AD.start_process(1)
            #else:
            #    self.AD.start_process(2)
            #print "set amplitude to ", amplitude, "V"
            
        def get_amplitude(self):
            if self.booted == False:
                return 0.0
            return self.AD.get_fpar(9)
        
        def reset(self):
            self.initialize()
        
        def get_error(self):
            return self.AD.get_last_error_text()
            
        def read(self):
            if self.booted == False:
                return None
            
            # initialize data array
            data = [0,0,0,0]
            
            # wait holdoff time
            sleep(self.holdoff)
                    
            # read output:
            # FPAR_1:     frequency (Hz)
            # FPAR_2:     X (digits)
            # FPAR_3:     Y
            self.fdet = self.AD.get_fpar(1)
            X = 2.0 * self.AD.get_fpar(2) * (20.0 / ((self.amplification + 1.0) * 65536.0))
            Y = 2.0 * self.AD.get_fpar(3) * (20.0 / ((self.amplification + 1.0) * 65536.0))
            
            # rotate by lock-in-phase
            data[0] = X * np.cos(self.PHI) + Y * np.sin(self.PHI)
            data[1] = -X * np.sin(self.PHI) + Y * np.cos(self.PHI)
            
            # calculate R and phi
            C = data[0] + 1j * data[1]                        # complex signal
            data[2] = np.absolute(C)                        # magnitude
            data[3] = np.angle(C)                            # phase
            self.phi = data[3]                                
            
            # data 0:X, 1:Y, 2:R, 3:PHI, 4:fdet
            return data
        
        def configure(self):
            dlg = ADWinLockInConfig(self)        
            if (dlg.ShowModal() == wx.ID_OK):
                dlg.get_configuration(self)
                if(dlg.autophase.GetValue() == True):
                    self.PHI = self.PHI + self.phi        # if autophase, copy last measured phase to config
                self.send_configuration()
            dlg.Destroy()
        
        def detect(self):
            retval = []
            if _support_ADWIN == True:
                try:
                    AD = adwin.adwin()
                    if AD.boot(input.ADDev, input.ADBoot) == 1:
                        retval.append(["ADWinLockIn", "ADWinLockIn", "1.0"])
                except:
                    pass
            return retval
    
    def widget(self, parent=None):
        try:
            return [InputWidget(parent,units=self.units, qtynames=self.qtynames, title=self.ID + ": " +self.name, input = self), AntennaWidget(parent,title=self.ID + ": antenna", amp = str(self.get_amplitude()), device = self)]
        except:
            return None

