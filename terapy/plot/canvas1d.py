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

    Canvas class for 1D plots

"""

from terapy.plot.base import PlotCanvas
from terapy.plot.plot1d import Plot1D
from wx.lib.pubsub import Publisher as pub
from terapy.filters import FilterBank
from terapy.core.axedit import AxisInfos, ConvertUnits, FormatUnits, du
import wxmpl
import matplotlib
import wx

class PlotCanvas1D(PlotCanvas,wxmpl.PlotPanel):
    """
    
        Canvas class for 1D plots

        Properties:
            is_data    -    if True, canvas is meant to display raw measurement data (bool)
            is_filter  -    if True, canvas is meant to display post-processed data (bool)
            dim        -    dimension of plots displayed on this canvas (int)
            name       -    name of canvas type (str)
    
    """
    name = "1D Plot"
    dim = 1
    def __init__(self, parent=None, id=-1, xlabel=AxisInfos("Delay",du["time"]), ylabel=AxisInfos("Signal",du["voltage"]), xscale="linear", yscale="linear"):
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
        
        self.Bind(wx.EVT_LEFT_DCLICK, self.OnLeftClick, self)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftClick, self)
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnRightClick, self)
    
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
    
    def OnRightClick(self, event):
        """
        
            Actions triggered on right mouse button click.
            
            Parameters:
                event    -    wx.Event
        
        """
        event.Skip()
        self.axes.set_autoscale_on(True)
        self.Update()

    def SetLabels(self):
        """
        
            Set axes labels.
        
        """
        self.axes.set_xlabel(self.labels[0].label())
        self.axes.set_ylabel(self.labels[1].label())
        for x in self.children:
            # set children units as a function of parent units and filter bank effect
            labels = [y.copy() for y in x.labels]
            old_labels = [y.copy() for y in x.labels]
            units = [FormatUnits(u) for u in x.bank.GetUnits([y.units for y in self.labels])]
            for u in units:u._magnitude=1.0
            for n in range(2): labels[n].units = units[n]
            
            ConvertUnits(x.labels, labels, ask_incompatible = False)
            for y in x.plots:
                y.array.Rescale(new_labels=labels, defaults=old_labels)
                y.SetData(y.array)
            # update units
            x.labels = labels
            x.Update()
    
    def Update(self, event=None):
        """
        
            Update canvas.
            
            Parameters:
                event    -    wx.Event
        
        """
        # update labels
        self.SetLabels()
        # update axes ranges
        self.axes.relim()
        try:
            # this can fail with invalid data (e.g. negative values with log scale)
            self.axes.autoscale_view()
        except:
            pass
        self.draw()
        
    def SetImage(self, n=1):
        """
        
            Set canvas tab icon.
            
            Parameters:
                n    -    icon index in parent image list (int)
        
        """
        PlotCanvas.SetImage(self, n)

    def AddPlot(self,array=None):
        """
        
            Add plot to canvas.
            
            Parameters:
                array    -    data array to be displayed (DataArray)
        
        """
        if self.is_filter:
            # if canvas is post-processing canvas, need to apply filter bank
            array = self.bank.ApplyFilters(array)
        # rescale array to plot units
        array.Rescale(self.labels)
        
        # add plot
        plt = Plot1D(self,array)
        self.plots.append(plt)
        for x in self.children:
            # if canvas has children, add plots to children too
            nplt = x.AddPlot(plt.array)
            nplt.source = plt
            plt.children.append(nplt)
        
        self.SetPlotColors()
        self.Update()
        return plt
    
    def RemovePlot(self, pos):
        """
        
            Remove given plot from canvas.
            
            Parameters:
                pos    -    plot index (int)
        
        """
        self.plots.pop(pos)
        self.SetPlotColors()
        self.Update()

    def Delete(self, event=None):
        """
        
            Delete canvas.
            
            Parameters:
                event    -    wx.Event
        
        """
        self.ClearCanvas()
        for x in self.children:
            x.Delete()
            x.children = []
        if self.source!=None:
            self.source.children.pop(self.source.children.index(self))
        pub.sendMessage("plot.empty_page", data=self)
    
    def SetPlotColors(self):
        """
        
            Set canvas plot colors.
        
        """
        # get number of arrays with custom color
        Nc = 0
        for x in self.plots:
            x.color = None
            if x.array!=None:
                if x.array.color!=None:
                    x.color = x.array.color
                    Nc+=1

        Np = len(self.plots)-Nc        
        np = Np-1
        for x in self.plots:
            if x.color != None:
                color = x.color
            else:
                color = (1.0-(np+1.0)/(Np*1.0),0.0,(np+1.0)/(Np*1.0))
                np -= 1
            if x.source==None:
                x.SetColor(color)
                y = x.children
                while len(y)>0:
                    for z in y:
                        z.SetColor(color)
                    y = y[-1].children
        
        # send color change event to notify history from change
        pub.sendMessage("plot.color_change")
    
    def AddFilterCanvas(self, fname = "", event=None):
        """
        
            Add post-processing canvas linked to current canvas.
            
            Parameters:
                fname    -    file name of post-processing filter bank (str, if none or invalid, load default bank)
                event    -    wx.Event
        
        """
        # add post-processing canvas if any adapted type available
        from terapy import plot
        for x in plot.canvas_modules:
            if x.dim == self.dim and x.is_filter:
                # found one, add suitable canvas
                cnv = x(self.parent)
                # must find where
                pos = self.parent.FindCanvas(self) + 1
                self.parent.InsertCanvas(cnv, pos, self.name + " (filtered)")
                # add reference to new canvas in current canvas children
                self.children.append(cnv)
                cnv.source = self
                # set filter bank
                bank = FilterBank(dim=self.dim)
                if fname=="":
                    bank.DefaultFilters()
                else:
                    bank.LoadFilterList(fname)
                if cnv.source!=None:
                    if cnv.source.is_filter:
                        bank.parent = cnv.source.bank
                        bank.parent.children.append(bank)
                cnv.SetFilterBank(bank)
                # adjust canvas units from source canvas + filter bank effect
                units = [FormatUnits(v) for v in bank.GetUnits([u.units for u in self.labels])]
                for x in units:x._magnitude=1.0
                for n in range(len(units)): cnv.labels[n].units = units[n]
                # if current canvas contains plots, add processed copies to new canvas
                for y in self.plots:
                    plt = cnv.AddPlot(y.array)
                    plt.SetColor(y.GetColor())
                    # set current plot as source to new plot
                    y.children.append(plt)
                    plt.source = y
                cnv.Update()
                break
    
    def RemoveFilterCanvases(self, event=None):
        """
        
            Remove post-processing canvases associated with this canvas.
            
            Parameters:
                event    -    wx.Event
        
        """
        # first remove cross-references between associated filter banks
        if self.is_filter:
            for x in self.bank.children:
                x.parent = None
            self.bank.children = []
        # then delete the canvas objects
        for x in self.children:
            x.RemoveFilterCanvases()
            x.Delete()
        self.children = []
