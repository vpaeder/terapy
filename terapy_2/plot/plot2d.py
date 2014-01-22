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

    Class for 2D plots

"""

from terapy.plot.base import Plot
from numpy import zeros
from wx.lib.pubsub import Publisher as pub

class Plot2D(Plot):
    """
    
        Class for 2D plots
    
    """
    def __init__(self, canvas=None, array=None):
        """
        
            Initialization.
            
            Parameters:
                canvas    -    parent canvas (PlotCanvas)
                array     -    plotted data array (DataArray)
        
        """
        Plot.__init__(self, canvas, array)
        self.SetData(array)
    
    def SetData(self, array):
        """
        
            Set plot data.
            
            Parameters:
                data     -    data array (DataArray)
        
        """
        self.array = array
        self.plot = array.data
    
    def GetData(self):
        """
        
            Get plot data.
            
            Output:
                data array (DataArray)
        
        """
        arr = self.array.Copy()
        arr.data = self.plot
        arr.shape = arr.data.shape
        return arr
    
    def Delete(self):
        """
        
            Delete plot.
        
        """
        self.array.plot = None
        self.canvas.Delete()
        pub.sendMessage("plot.color_change")
    
    def SetName(self, name="Plot"):
        """
        
            Set plot name.
            
            Parameters:
                name    -    name (str)
        
        """
        self.name = name # don't do anything with that at the moment (may be for legend)
