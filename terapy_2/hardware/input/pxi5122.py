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

    Device driver for National Instruments PXI-5122 DAQ card
 
"""

from terapy.hardware.input.base import InputDevice
from time import sleep, clock
from math import sqrt, tan
import numpy as np
from scipy.integrate import simps
from scipy.fftpack import fft

# NI PXI interface
try:
    from pyPXI5122 import *
    _support_PXI = True
except:
    _support_PXI = False    

# apply 2nd order bessel filter to X; Fg = f3dB / fSample
# see Tietze, Schenk book for details
def besselfilter(X, Fg):
    if(len(X) < 3):
        return (X[0] + X[1]) / 2.0
    if(Fg == 0):
        Fg = 1.0
    a1 = 1.3617
    b1 = 0.6180
    l = 1.0 / tan(3.14159 * Fg)    
    Y = []

    # get filter coefficients
    alpha0 = 1.0 / (1.0 + a1 * l + b1 * l * l)
    beta1 = 2.0 * (1.0 - b1 * l *l) / (1 + a1 * l + b1 * l * l)
    beta2 = (1.0 - a1 * l + b1 * l *l) / (1 + a1 * l + b1 * l * l)

    # filter data
    Y.append(X[0])
    Y.append(X[1])
    for i in range(2, len(X)):
        Y.append(alpha0 * ( X[i] + 2.0 * X[i-1] + X[i-2] ) - beta1 * Y[i-1] - beta2 * Y[i-2])
    
    # return last value as averaged value
    return Y[-1];


if _support_PXI:
    # ###################################################################################    
    # NI PXI-5122
    # special mode: take 3 samples per trigger pulse: ref1, thz, ref2
    from pxi5122_config import *
    PXI_TIMEOUT = 1.0    # 1s timeout for PXI        
            
    class PXI5122(InputDevice):
        def __init__(self):
            InputDevice.__init__(self)
            self.config = ['holdoff', 'refpos', 'records', 'trig_delay', 'trig_level', 'trig_slope', 'ch0_impedance', 'ch0_range', 'ch0_offset', 'ch1_impedance', 'ch1_range', 'ch1_offset', 'intmode', 'inttime', 'refmode', 'CH1mode', 'modlevel', 'gatewidth']
            self.holdoff = 0.0
            self.refpos = 0
            self.records = 1
            self.trig_delay = 0.0
            self.trig_level = 0.0
            self.trig_slope = -1
            self.ch0_impedance = 1000000
            self.ch0_range = 20.0
            self.ch0_offset = 0.0
            self.ch1_impedance = 1000000
            self.ch1_range = 20.0
            self.ch1_offset = 0.0
            self.intmode = 0
            self.inttime = 30.0
            self.refmode = 3
            self.CH1mode = 0
            self.modlevel = 0.0
            self.gatewidth = 1.0
            # device handle
            self.pxi = pyPXI5122()
            self.units = ["V"]
            self.qtynames = [""]
        
        def __del__(self):
            # reset ext clk to intern
            self.pxi.config_clock(0)
            # close session on exiting the program
            self.pxi.close_session()
        
        def initialize(self):
            # establish a connection
            self.pxi.close_session()
            if self.pxi.open_session(self.address) == 1:
                print "initiated PXI5122 on port", self.address    
            else:
                print self.pxi.get_error()
                raise    # raise at least some type of exception to indicate an error to the hardware module
            # now configure the device
            self.send_configuration()
        
        def reset(self):
            # close session first
            self.pxi.close_session()
            # then re-initialize
            self.initialize()
        
        def send_configuration(self):
            # configure timing - max sample rate, force realtime, reference and number of records from config
            # 'refmode' is 3 or 5 depending on the modus of referencing the signal
            self.pxi.config_horizontal(100000000, self.refmode, self.refpos, self.records, True)
            
            # trigger from EXT. TRIG, level and slope from config, coupling DC, holdoff and delay 0.0
            self.pxi.config_trigger_edge(2, self.trig_level, self.trig_slope, 1, 0.0, self.trig_delay)
            
            # config sample clock    -    uncomment only in production state!
            #self.pxi.config_clock(0)
            self.pxi.config_clock(1)
            
            # configure channels
            # no filters, coupling is dc, impedance, range and offset from config, no probe attenuation and both channels enabled
            self.pxi.config_channel(0, self.ch0_impedance, -1, self.ch0_range, self.ch0_offset, 1, 1, True)
            self.pxi.config_channel(1, self.ch1_impedance, -1, self.ch1_range, self.ch1_offset, 1, 1, True)
            
        def get_error(self):
            return self.pxi.get_error()
            
        def read(self):    
            # leave if no connection is present
            if self.pxi.session_open() == False:
                return None
            data0 = []
            data1 = []
            data2 = []
            data3 = []
                
            # wait holdoff time
            sleep(self.holdoff)
            
            # start acquisition and wait for completion
            self.pxi.start()
            startT = clock()
            while(self.pxi.completed() != 1 and clock() < startT + PXI_TIMEOUT):
                sleep(0.01)
            if(clock() > startT + PXI_TIMEOUT):
                return None
            
            # read both channels' raw data
            dummy, dataCH0 = self.pxi.fetch_channel_raw(0)
            dummy, dataCH1 = self.pxi.fetch_channel_raw(1)
            # get number of records and number of samples
            # data order is R1S1 R1S2 .. R1SN R2S1 .. RMSN
            NS = self.refmode
            NR = self.records
            
            if(len(dataCH0) < NS * NR):
                return None
            
            if self.CH1mode == 2:    # normalize each input pulse by the corresponding pulse from CH1                
                for i in range(NR * NS):
                    if(dataCH1[i] != 0.0):
                        dataCH0[i] = dataCH0[i] / dataCH1[i]
                    else:
                        dataCH0[i] = dataCH0[i] / 1.0e-10
            
            if self.CH1mode == 4:    # A-B: calculate the difference signal digitally
                for i in range(NR * NS):
                    dataCH0[i] = dataCH0[i] - dataCH1[i]
            
            # in gated mode, read the value of the gate pulse first
            # use the same referencing mode as for the signal input
            gatemin = -10.0
            gatemax = 10.0
            if self.CH1mode == 3:
                for i in range(NR):
                    if(NS == 3):    # use just the sample that corresponds to the 1kHz pulse
                        valueCH1 = dataCH1[NS * i + 1] - 0.5 * (dataCH1[NS * i + 0] + dataCH1[NS * i + 2])
                    else:            # just use 5 samples and calculate ref as avg over the two before and after 
                        #valueCH1 = dataCH1[NS * i + 2] - 0.25 * (dataCH1[NS * i + 0] + dataCH1[NS * i + 1] + dataCH1[NS * i + 3] + dataCH1[NS * i + 4])
                        valueCH1 = dataCH1[NS * i + 2] - 0.5 * (dataCH1[NS * i + 0] + dataCH1[NS * i + 4])
                    data1.append(valueCH1)
            
                # get mean and standard deviation
                mean = 0.0
                for i in range(NR):
                    mean += data1[i]
                mean /= float(NR)
                sigma = 0.0
                if(NR > 1):                    
                    for i in range(NR):
                        sigma += (data1[i] - mean)**2                    
                    sigma = sqrt(sigma / (NR - 1))
                gatemin = mean - sigma * self.gatewidth
                gatemax = mean + sigma * self.gatewidth
                
            # calculate the input signal
            for i in range(NR):
                if(NS == 3):    # use two samples, one before and one after the main pulse
                    valueCH0 = dataCH0[NS * i + 1] - 0.5 * (dataCH0[NS * i + 0] + dataCH0[NS * i + 2])                
                else:            # just use 5 samples and calculate ref as avg over the two before and after 
                    #valueCH0 = dataCH0[NS * i + 2] - 0.25 * (dataCH0[NS * i + 0] + dataCH0[NS * i + 1] + dataCH0[NS * i + 3] + dataCH0[NS * i + 4])                
                    valueCH0 = dataCH0[NS * i + 2] - 0.5 * (dataCH0[NS * i + 0] + dataCH0[NS * i + 4])                
                if(self.CH1mode != 2 or (valueCH0 >= gatemin and valueCH0 <= gatemax)):
                    data0.append(valueCH0)
            # and the CH1 signal
            if self.CH1mode == 1:
                for i in range(NR):
                    if(NS == 3):    # use two samples, one before and one after the main pulse
                        valueCH1 = (dataCH1[NS * i + 0] + dataCH1[NS * i + 1] + dataCH1[NS * i + 2]) / 3
                    else:            # just use 5 samples and calculate ref as avg over the two before and after 
#                        valueCH1 = (dataCH1[NS * i + 0] + dataCH1[NS * i + 1] + dataCH1[NS * i + 2] + dataCH1[NS * i + 3] + dataCH1[NS * i + 4]) / 5                
                        valueCH1 = (dataCH1[NS * i + 0] + dataCH1[NS * i + 2] + dataCH1[NS * i + 4]) / 3
                    data1.append(valueCH1)
                    if(valueCH1 > self.modlevel):
                        data3.append(data0[i])    # store "negative" data    
                        #print "p"
                    else:
                        data2.append(data0[i])    # store "positive" data
                        #print "n"
            
            # averaging - put here the correct input assignment!!
            value0 = 0.0
            value2 = 0.0
            value3 = 0.0
            if(self.intmode == 0):    # just average
                if(self.CH1mode == 1):# do this for all three arrays
                    for i in range(len(data2)):
                        value2 += data2[i]
                    for i in range(len(data3)):
                        value3 += data3[i]
                    if(len(data2) > 1):
                        value2 /= float(len(data2))
                    if(len(data3) > 1):
                        value3 /= float(len(data3))
                    value0 = value2 - value3
                else:
                    for i in range(len(data0)):
                        value0 += data0[i]
                    if(len(data0) > 1):
                        value0 /= float(len(data0))
            else:                                # use bessel filter
                if(self.CH1mode == 1):
                    value2 = besselfilter(data2, 1.0 / float(self.inttime))
                    value3 = besselfilter(data3, 1.0 / float(self.inttime))
                    value0 = value2 - value3
                else:
                    value0 = besselfilter(data0, 1.0 / float(self.inttime))
                
            return [value0, value2, value3]
        
        def configure(self):
            if self.pxi.session_open() == False:
                print "ERROR: No connection to PXI5122! Rescan Hardware!"
                return
            dlg = PXI5122config(self.config)        
            if (dlg.ShowModal() == wx.ID_OK):            
                self.config = dlg.get_configuration()
                self.send_configuration()
            dlg.Destroy()
            
    # #############################################################################################################
    # PXI 5122 Lock-In emulator
    # signal and reference are numpy arrays with equal number of elements
    # phi is the desired lock-in phase for the X and Y components
    # return value is [X, Y, R, dphi]
    def sign(a):
        if(a > 0.0):
            return 1
        else:
            return -1
            
    def simple_lock_in(signal, reference, phi0):
        if len(reference) != len(signal):
            print "sample length of signal and reference is different!"
            return [0, 0, 0, 0]
            
        # substract offset from reference signal to get clear zero passes
        reference = reference - (np.amax(reference) + np.amin(reference))/2.0
        #reference = reference - np.sum(reference)/float(len(reference))
        
        # get periodicity and reference frequency by counting the zero passes
        i = 0
        pm = sign(reference[i])
        while(pm == sign(reference[i])):
            i = i + 1
        iorig = i
        iend = i
        pmorig = sign(reference[iorig])
        pm = sign(reference[iorig])
        Np = 0
        for i in range(iorig, len(reference)):
            if(sign(reference[i]) != pm and sign(reference[i]) == pmorig):
                iend = i
                Np = Np + 1
            pm = sign(reference[i])
        period = float(iend - iorig) / float(Np)
        fdet = 1.0 / period

        # create reference sine and cosine waveforms with zero phase
        if(reference[0] > 0):
            phi0 = phi0 + np.pi
        time = np.arange(len(reference))
        refs = 2.0 * np.sin(2.0 * np.pi * fdet * (time-iorig) + phi0)    # the factor 2 accounts for the fact that the returned signal is half the peak signal
        refc = 2.0 * np.cos(2.0 * np.pi * fdet * (time-iorig) + phi0)
        
        # multiply with input signal
        sigs = signal * refs
        sigc = signal * refc

        # perform averaging
        X = simps(sigs[iorig:iend]) / float(iend-iorig)        # = A0/2 * cos(dphi)
        Y = simps(sigc[iorig:iend]) / float(iend-iorig)        # = A0/2 * sin(dphi)
        #X = np.sum(sigs[iorig:iend]) / float(iend-iorig)        # = A0/2 * cos(dphi)
        #Y = np.sum(sigc[iorig:iend]) / float(iend-iorig)        # = A0/2 * sin(dphi)

        C = X + 1j * Y                                    # complex signal
        R = np.absolute(C)                                # magnitude
        dphi = np.angle(C)                                # phase

        return [X, Y, R, dphi, fdet]

    def lock_in(signal, reference, phase):
        N = len(reference)
        
        # prepare reference - subtract dc offset
        R = reference #- np.sum(reference) / float(N)

        # multiply with window function (half sinus)
        window = np.sin(np.pi / float(N) * np.arange(N)) 
        R = R * window
        
        # get FFT
        R = fft(R)[0:N/2]
        
        i0 = np.argmax(np.absolute(R))            # highest amplitude frequency
        # get frequency estimate by interpolation over three adjacent points
        f0 = float(i0) + 0.5 * (-np.absolute(R[i0+1]) + np.absolute(R[i0-1])) / (np.absolute(R[i0-1]) + np.absolute(R[i0+1]) - 2.0 * np.absolute(R[i0]))
        phi0 = np.angle(R[i0])                    # phase

        # calculate in and out-of-phase components
        time = np.arange(N) / float(N)
        refs = 2.0 * np.sin(2.0 * np.pi * f0 * time + phi0 + phase)
        refc = 2.0 * np.cos(2.0 * np.pi * f0 * time + phi0 + phase)
        
        # multiply both components
        #S = signal #* window
        sigs = signal * refs
        sigc = signal * refc

        # perform averaging
        X = simps(sigs) / float(N)
        Y = simps(sigc) / float(N)

        C = X + 1j * Y                                    # complex signal
        R = np.absolute(C)                                # magnitude
        phi = np.angle(C)                                # phase
        
        return [X, Y, R, phi, f0 / float(N)]

        def detect(self):
            retval = []
            if _support_PXI == True:
                # attempt to connect to PXI devices
                pxi = pyPXI5122()
                for i in range(1,3):        # pxi counter
                    for j in range(1,8):    # slot counter
                        # create address string - maybe you have to adjust for different systems
                        handle = "PXI%dSlot%d" % (i, j)
                        try:
                            if(pxi.open_session(handle) == 1):
                                # found a device
                                retval.append([handle,"PXI5122", handle])
                                
                                pxi.close_session()
                        except:
                            pass
            return retval
        
    # the PXI5122LockIn class
    class PXI5122LockIn(InputDevice):
        def __init__(self):
            InputDevice.__init__(self)
            # signal = 0:X, 1:Y, 2:R, 3:PHI
            # PHI is phase for lock-in detection in rad
            self.config = {'signal':0, 'PHI':0.0, 'holdoff':0.0, 'ch0_impedance':1000000, 'ch0_filter':-1, 'ch0_range':20.0, 'ch0_offset':0.0, 'ch1_impedance':1000000, 'ch1_filter':-1, 'ch1_range':20.0, 'ch1_offset':0.0, 'inttime':300.0}
            self.fdet = 0.0    # detected frequency in Hz
            self.phi = 0.0  # last detected phase in rad
            self.units = ["V", "V", "V", "deg", "Hz"]
            self.qtynames = ["X","Y","R","Phi","f"]
            
            # device handle
            self.pxi = pyPXI5122()
        
        def __del__(self):
            # reset ext clk to intern
            #self.pxi.config_clock(0)
            # close session on exiting the program
            self.pxi.close_session()
        
        def initialize(self):
            # establish a connection
            self.pxi.close_session()
            if self.pxi.open_session(self.address) == 1:
                print "initiated PXI5122LockIn on port", self.address    
            else:
                print self.pxi.get_error()
                raise    # raise at least some type of exception to indicate an error to the hardware module
            # now configure the device
            self.send_configuration()
        
        def config2string(self):
            sep0 = "$"
            sep1 = "##"
            keys = sep0.join(self.config.keys())
            values = sep0.join(map(lambda x: str(x), self.config.values()))
            return sep1.join([keys, values])
            
        def string2config(self, configstring):
            keys, values = configstring.split("##")
            keys = keys.split("$")
            values = values.split("$")
            for i in range(len(keys)):
                if(isinstance(self.config[keys[i]], int)):
                    try:
                        self.config[keys[i]] = int(values[i])
                    except:
                        self.config[keys[i]] = float(values[i])    
                else:
                    self.config[keys[i]] = float(values[i])    
        
        def reset(self):
            # close session first
            self.pxi.close_session()
            # then re-initialize
            self.initialize()
        
        def send_configuration(self):
            fsample = 100e3            # sample rate in Hz
            # we target a modulation frequency between 1 and 10kHz,
            # for 100kHz sample rate, this amounts to at least 5 points per period 
            
            # configure timing - max sample rate, force realtime
            # 'inttime' is integration time in ms; converted to number of samples
            self.pxi.config_horizontal(fsample, int(self.inttime * 1e-3 * fsample), 0.0, 1, True)

            # configure channels
            # coupling is ac, impedance, range, filters and offset from config, no probe attenuation and both channels enabled
            self.pxi.config_channel(0, self.ch0_impedance, self.ch0_filter, self.ch0_range, self.ch0_offset, 0, 1, True)
            self.pxi.config_channel(1, self.ch1_impedance, self.ch1_filter, self.ch1_range, self.ch1_offset, 0, 1, True)
            
            # trigger immediately
            self.pxi.config_trigger_immediate()
            #self.pxi.config_trigger_edge(1, 0.0, 1, 1, 0.0, 0.0)
            
            # config sample clock to internal
            self.pxi.config_clock(0)    # when clocking to the 80MHz laser, the frequencies are not valid any more        
            
        def get_error(self):
            return self.pxi.get_error()
            
        def read(self):    
            # leave if no connection is present
            if self.pxi.session_open() == False:
                return None
        
            data0 = []
            data1 = []
            data2 = []
            data3 = []
            
            # wait holdoff time
            sleep(self.holdoff)
            
            # start acquisition and wait for completion
            self.pxi.start()
            startT = clock()
            while(self.pxi.completed() != 1 and clock() < startT + self.inttime * 1e-3 + PXI_TIMEOUT):
                sleep(0.01)
            if(clock() > startT + PXI_TIMEOUT):
                return None
            
            # read both channels' raw data
            time, dataCH0 = self.pxi.fetch_channel_raw(0)    # signal
            time, dataCH1 = self.pxi.fetch_channel_raw(1)    # reference
            
            # in lock-in mode, only 1 record is sampled
            #data = simple_lock_in(dataCH0, dataCH1, self.PHI)
            data = lock_in(dataCH0, dataCH1, self.PHI)
            # data 0:X, 1:Y, 2:R, 3:PHI, 4:fdet
            
            self.fdet = data[4] * float(len(time) - 1) / (time[-1] - time[0])    # detected frequency in Hz
            self.phi = data[3]
            
            data[4] = self.fdet
            
            return data
        
        def configure(self):
            if self.pxi.session_open() == False:
                print "ERROR: No connection to PXI5122! Rescan Hardware!"
                return
            dlg = PXI5122LockInConfig(self.config)        
            if (dlg.ShowModal() == wx.ID_OK):
                self.config = dlg.get_configuration()
                if(dlg.autophase.GetValue() == True):
                    self.PHI = self.PHI + self.phi        # if autophase, copy last measured phase to config
                self.send_configuration()
            dlg.Destroy()
    
        def detect(self):
            retval = []
            if _support_PXI == True:
                # attempt to connect to PXI devices
                pxi = pyPXI5122()
                for i in range(1,3):        # pxi counter
                    for j in range(1,8):    # slot counter
                        # create address string - maybe you have to adjust for different systems
                        handle = "PXI%dSlot%d" % (i, j)
                        try:
                            if(pxi.open_session(handle) == 1):
                                # found a device
                                retval.append([handle,"PXI5122LockIn", handle])
                                
                                pxi.close_session()
                        except:
                            pass
            return retval
