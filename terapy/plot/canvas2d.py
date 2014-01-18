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

    Canvas class for 2D plots

"""

from terapy.plot.base import PlotCanvas
from wx.lib.pubsub import Publisher as pub
from matplotlib.colors import LinearSegmentedColormap
from terapy.plot.plot2d import Plot2D
from terapy.core.axedit import AxisInfos, FormatUnits, du
import wxmpl
import wx
import matplotlib

class PlotCanvas2D(PlotCanvas,wxmpl.PlotPanel):
    """
    
        Canvas class for 2D plots

        Properties:
            is_data    -    if True, canvas is meant to display raw measurement data (bool)
            is_filter  -    if True, canvas is meant to display post-processed data (bool)
            dim        -    dimension of plots displayed on this canvas (int)
            name       -    name of canvas type (str)
    
    """
    is_data = True
    name = "2D Plot"
    dim = 2
    def __init__(self, parent=None, id=-1, xlabel=AxisInfos("Delay",du["time"]), ylabel=AxisInfos("Distance",du["length"]), xscale="linear", yscale="linear"):
        """
        
            Initialization.
            
            Parameters:
                parent    -    parent window (wx.Window)
                id        -    id (int)
                xlabel    -    label and units of abscissa axis (terapy.axedit.AxisInfos)
                ylabel    -    label and units of ordinate axis (terapy.axedit.AxisInfos)
                xscale    -    abscissa scale type (linear or log)
                yscale    -    ordinate scale type (linear or log)
        
        """
        wxmpl.PlotPanel.__init__(self,parent,id)
        PlotCanvas.__init__(self,parent,id)
        
        fig = self.get_figure()
        self.axes = fig.gca()
        self.axes.grid(True)
        self.axes.set_autoscale_on(True)
        self.axes.set_xscale(xscale)
        self.axes.set_yscale(yscale)
        
        # must make a copy of labels, otherwise same instance is used for every plot
        xlabel = xlabel.copy()
        ylabel = ylabel.copy()

        # re-format axis units into current default units 
        xlabel.units = FormatUnits(xlabel.units)
        ylabel.units = FormatUnits(ylabel.units)
        for x in [xlabel,ylabel]: x.units._magnitude = 1.0
        self.labels = [xlabel, ylabel]
        self.SetLabels()
        
        self.dim = 2
        self.set_zoom(False)
        self.set_location(False)
        self.set_selection(False)
        # generate colormap
        cdict = {'red': ((0.0, 0.0, 0.0),(0.5, 1.0, 1.0),(1.0, 1.0, 0.0)),
                'green': ((0.0, 0.0, 0.0),(0.5, 1.0, 1.0),(1.0, 0.0, 0.0)),
                'blue': ((0.0, 0.0, 1.0),(0.5, 1.0, 1.0),(1.0, 0.0, 0.0))}
        self._2d_cmap = LinearSegmentedColormap('my_colormap',cdict,256)        
        cdict = {'red': ((0.0, 0.0, 1.0),(1.0, 1.0, 0.0)),
                'green': ((0.0, 0.0, 1.0),(1.0, 0.0, 0.0)),
                'blue': ((0.0, 0.0, 1.0),(1.0, 0.0, 0.0))}
        self._2d_cmap_pos = LinearSegmentedColormap('my_colormap_pos',cdict,256)
        
        cdict = {'red': ((0.0, 0.0, 0.0),(1.0, 1.0, 0.0)),
                'green': ((0.0, 0.0, 0.0),(1.0, 1.0, 0.0)),
                'blue': ((0.0, 0.0, 1.0),(1.0, 1.0, 0.0))}
        self._2d_cmap_neg = LinearSegmentedColormap('my_colormap_neg',cdict,256)

        # send color change event to notify history from change
        pub.sendMessage("plot.color_change")

        self.Bind(wx.EVT_LEFT_DCLICK, self.OnLeftClick, self)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftClick, self)
    
    def Destroy(self):
        PlotCanvas.Destroy(self)
        wxmpl.PlotPanel.Destroy(self)
    
    def OnLeftClick(self, event):
        """
        
            Actions triggered on left mouse button click.
            
            Parameters:
                event    -    wx.Event
        
        """
        # MPL plot canvas intercept double clicks
        # Use another strategy:
        #    - on 1st click, set a timer
        #    - if timer triggers before 2nd click, resets
        #    - if click happens before, consider as double click
        if hasattr(self,'timer'):
            self.timer.Stop()
            del(self.timer)
            dbl = True
        else:
            self.timer = wx.Timer()
            self.timer.Bind(wx.EVT_TIMER, self.OnLeftClick, self.timer)
            self.timer.Start(500)
            dbl = False
            event.Skip()
        
        if not(isinstance(event,wx.TimerEvent)):
            if dbl or event.ButtonDClick():
                x, y = self._get_canvas_xy(event)
                evt = matplotlib.backend_bases.MouseEvent(1, self, x, y)
                for ax in self.get_figure().get_axes(): 
                    xlabel = ax.xaxis.get_label()
                    ylabel = ax.yaxis.get_label()
                    if xlabel.contains(evt)[0] or ylabel.contains(evt)[0]:
                        self.EditAxes()

    def AddPlot(self,array=None):
        """
        
            Add plot to canvas.
            
            Parameters:
                array    -    data array to be displayed (DataArray)
        
        """
        self.is_full = True
        array.Rescale(self.labels)
        plt = Plot2D(self,array)
        self.plots.append(plt)
        self.SetPlotColors()
        self.Update()
        return plt
    
    def SetLabels(self):
        """
        
            Set axes labels.
        
        """
        self.axes.set_xlabel(self.labels[0].label())
        self.axes.set_ylabel(self.labels[1].label())
    
    def Update(self, event=None):
        """
        
            Update canvas.
            
            Parameters:
                event    -    wx.Event
        
        """
        if len(self.plots)>0:
            # get new instance
            self.get_figure().clear()
            fig = self.get_figure()
            self.axes = fig.gca()
            # plot data
            extent = [min(self.plots[0].array.coords[0]), max(self.plots[0].array.coords[0]), min(self.plots[0].array.coords[1]), max(self.plots[0].array.coords[1])]
            plt = self.axes.imshow(self.plots[0].array.data, origin='lower', cmap=self._2d_cmap, interpolation='nearest', extent = extent, aspect="auto")
            # autoscale and generate colorbar
            self.axes.set_aspect('auto')
            self.axes.set_autoscale_on(True)
            self.axes.autoscale_view(True,False,False)
            fig.colorbar(plt,format="%0.1e")
            self.SetLabels()
            # redraw
            self.draw()
    
    def Delete(self, event=None):
        """
        
            Delete canvas.
            
            Parameters:
                event    -    wx.Event
        
        """
        if len(self.plots)>0:
            while len(self.plots)>0:
                plt = self.plots.pop()
                plt.Delete()
            if len(self.plots)==0:
                pub.sendMessage("plot.empty_page", data=self)
    
    def PopupMenuItems(self,menu):
        """
        
            Add popup menu items for canvas to given menu.
            
            Parameters:
                menu    -    wx.Menu
        
        """
        mitem = menu.Append(wx.NewId(),"&Edit axes")
        menu.Bind(wx.EVT_MENU, self.EditAxes, id=mitem.Id)
    
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
