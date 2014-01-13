#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2013  Vincent Paeder
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

    Custom interface threads

"""

import threading
from time import sleep
from terapy.core import refresh_delay
from wx.lib.pubsub import Publisher as pub
import wx

class ScanThread(threading.Thread):
    """
    
        Thread active during scan sequence.
    
    """
    def __init__(self, sequence, meas):
        """
        
            Initialization.
            
            Parameters:
                sequence  -    scan sequence (ScanEvent)
                meas      -    measurement container (Measurement)
        
        """
        threading.Thread.__init__(self)
        self.meas = meas # data container (Measurement)
        self.sequence = sequence # associated sequence (ScanEvent)
    
    def run(self):
        """
        
            Run thread.
        
        """
        # start progress display thread
        pthread = ProgressThread(self.meas)
        pthread.start()
        
        # run sequence
        self.sequence.run(self.meas)
        
        # stop progress thread
        while pthread.is_alive():
            sleep(0.01)
        pthread = None
        
        # announce measurement end
        wx.CallAfter(pub.sendMessage, "scan.after", data=self.meas)
    
class ProgressThread(threading.Thread):
    """
    
        Thread responsible for updating progress status during measurement.
    
    """
    def __init__(self, meas):
        """
        
            Initialization.
            
            Parameters:
                meas      -    measurement container (Measurement)
        
        """
        threading.Thread.__init__(self)
        self.meas = meas
        self.can_run = True
        pub.subscribe(self.stop, "scan.stop")
    
    def progress(self):
        """
        
            Return associated measurement progress.
            
            Output:
                progress, in percent
        
        """
        return self.meas.current*100/self.meas.total
        
    def run(self):
        """
        
            Run thread.
        
        """
        while self.can_run:
            sleep(refresh_delay)
            wx.CallAfter(pub.sendMessage,"progress_change",data=self.progress())
    
    def stop(self,inst=None):
        """
        
            Stop thread.
            
            Parameters:
                inst    -    pubsub event data
                             inst.data must be boolean
        
        """
        self.can_run = False
