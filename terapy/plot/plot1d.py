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

    Class for 1D plots

"""

from terapy.plot.base import Plot
from matplotlib.lines import Line2D
from wx.lib.pubsub import Publisher as pub

class Plot1D(Plot):
    """
    
        Class for 1D plots
    
    """
    def __init__(self, canvas=None, array=None):
        """
        
            Initialization.
            
            Parameters:
                canvas    -    parent canvas (PlotCanvas)
                array     -    plotted data array (DataArray)
        
        """
        Plot.__init__(self, canvas, array)
        self.plot = Line2D([],[])
        self.canvas.axes.add_line(self.plot)
        self.SetData(array)
        self.plot.set_visible(True)

    def SetData(self, array):
        """
        
            Set plot data.
            
            Parameters:
                data     -    data array (DataArray)
        
        """
        self.array = array
        self.plot.set_data(array.coords[0],array.data)
    
    def GetData(self):
        """
        
            Get plot data.
            
            Output:
                data array (DataArray)
        
        """
        arr = self.array.Copy()
        arr.coords[0], arr.data = self.plot.get_data()
        arr.shape = arr.data.shape
        return arr

    def SetColor(self, col):
        """
        
            Set plot color.
            
            Parameters:
                col    -    color (wx.Color)
        
        """
        Plot.SetColor(self, col)
        color = (self.color.red/255.0,self.color.green/255.0,self.color.blue/255.0)
        self.plot.set_color(color)
    
    def Delete(self):
        """
        
            Delete plot.
        
        """
        self.plot.remove()
        if self.source!=None:
            try:
                idx = self.source.children.index(self)
                self.source.children.pop(idx)
            except:
                pass
        else:
            self.array.plot = None
        if self.canvas.plots.count(self)>0:
            idx = self.canvas.plots.index(self)
            self.canvas.RemovePlot(idx)
        for x in self.children:
            x.Delete()
        self.children = []
        pub.sendMessage("plot.color_change")
    
    def SetName(self, name="Plot"):
        """
        
            Set plot name.
            
            Parameters:
                name    -    name (str)
        
        """
        self.name = name # don't do anything with that at the moment (may be for legend)
