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

    Example of Plot class

"""

from terapy.plot.base import Plot

class PlotExample(Plot):
    """
    
        Example of Plot class
    
    """
    def __init__(self, canvas=None, array=None):
        """
        
            Initialization.
            
            Parameters:
                canvas    -    parent canvas (PlotCanvas)
                array     -    plotted data array (DataArray)
        
        """
        Plot.__init__(self, canvas, array)
        self.plot = None
        self.array = array
        self.SetData(array)

    def SetData(self, array):
        """
        
            Set plot data.
            
            Parameters:
                data     -    data array (DataArray)
        
        """
        # Insert here what should be done to set plot data from given DataArray.
        # DataArray shape, data and coords variables may be useful here.
        # See DataArray documentation for details.
        pass
    
    def GetData(self):
        """
        
            Get plot data.
            
            Output:
                data array (DataArray)
        
        """
        return self.array

    def SetColor(self, col):
        """
        
            Set plot color.
            
            Parameters:
                col    -    color (wx.Color)
        
        """
        Plot.SetColor(self, col)
    
    def Delete(self):
        """
        
            Delete plot.
        
        """
        # Insert here what should be done when plot is deleted.
        self.canvas.RemovePlot(self)
    
    def SetName(self, name="Plot"):
        """
        
            Set plot name.
            
            Parameters:
                name    -    name (str)
        
        """
        self.name = name # don't do anything with that at the moment (may be for legend)
