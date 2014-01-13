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

    Example of plot canvas class

"""

from terapy.plot.base import PlotCanvas

class PlotCanvasExample(PlotCanvas):
    """
    
        Example of plot canvas class

        Properties:
            is_data    -    if True, canvas is meant to display raw measurement data (bool)
            is_filter  -    if True, canvas is meant to display post-processed data (bool)
            dim        -    dimension of plots displayed on this canvas (int)
            name       -    name of canvas type (str)
    
    """
    is_data = True
    name = "Example plot"
    dim = -1
    def __init__(self, parent=None, id=-1, xlabel="Delay (ps)", ylabel="Distance (um)", xscale="linear", yscale="linear"):
        """
        
            Initialization.
            
            Parameters:
                parent    -    parent window (wx.Window)
                id        -    id (int)
                xlabel    -    label of abscissa axis (str)
                ylabel    -    label of ordinate axis (str)
                xscale    -    abscissa scale type (linear or log)
                yscale    -    ordinate scale type (linear or log)
        
        """
        PlotCanvas.__init__(self,parent,id, xlabel, ylabel, xscale, yscale)
    
    def AddPlot(self,array=None):
        """
        
            Add plot to canvas.
            
            Parameters:
                array    -    data array to be displayed (DataArray)
        
        """
        # Insert here what should be done to convert DataArray to plot supported by this canvas.
        # DataArray shape, data and coords variables may be useful here.
        # See DataArray documentation for details.
        pass
    
    def Update(self, event=None):
        """
        
            Update canvas display.
            
            Parameters:
                event    -    wx.Event
        
        """
        pass
    
    def Delete(self, event=None):
        """
        
            Delete canvas.
            
            Parameters:
                event    -    wx.Event
        
        """
        # Insert here what should be done when canvas is deleted.
        # E.g. delete associated plots, destroy associated window, ...
        for x in self.plots:
            self.RemovePlot(x)
    
    def SetName(self, name="Plot"):
        """
        
            Set canvas tab name.
            
            Parameters:
                name    -    name (str)
        
        """
        idx = self.parent.FindCanvas(self)
        if idx>-1:        
            self.parent.SetPageText(idx,name)
    
    def SetImage(self, n=2):
        """
        
            Set canvas tab icon.
            
            Parameters:
                n    -    icon index in parent image list (int)
        
        """
        PlotCanvas.SetImage(self, n)
