#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010-2013 D. Dietze, 2013-2014  Vincent Paeder
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

    TeraPy - Graphical user interface for Terahertz Time-domain Spectroscopy 
    (c) 2010-2013, Daniel Dietze, 2013-2014 Vincent Paeder

"""

# imports
# wx for general GUI
import wx
from terapy.core.splitter import Splitter
from terapy.core.menus import GetItemIds
from wx.lib.pubsub import Publisher as pub
# plotting and data treatment
from terapy.filters.control import FilterControl
from terapy.plot.notebook import PlotNotebook
# filesystem handling
from terapy.core import user_path
import os
# hardware stuff
import hardware
# scan-related stuff
from time import localtime, strftime
from terapy.scan.control import ScanEventList
from terapy.core.history import HistoryControl
from terapy.core import icon_path

__version__         = "2.00b5 / 20.01.2014"
__doc_url__         = "http://128.131.79.22/terapy/doc.html"

class TeraPyMainFrame(wx.Frame):
    def __init__(self):
        """
        
            Initialization.
        
        """
        wx.Frame.__init__(self, None, -1, "TeraPy", size=(1000, 750))
        self.icon = wx.Icon(icon_path + "teraicon.ico", wx.BITMAP_TYPE_ICO)
        self.SetIcon(self.icon)
        
        self.panel = wx.Panel(self)
        
        #
        self.is_scanning = False
        
        # statusbar
        self.CreateStatusBar(2)
        self.SetStatusWidths([-1, 180])
        wx.CallAfter(pub.sendMessage,"set_status_text","Welcome to TeraPy")
        
        # restore device informations
        hardware.restore_hardware_info()
        
        # create menu bar - this requires that the devices are already loaded
        self.__create_menu()
        
        # create and add top-level widgets
        self.__create_widgets()
                
        # arrange objects and set layout
        self.__set_properties()
        self.__do_layout()
        
        # widget event bindings
        self.__create_event_bindings()
    
        # check for time axis
        self.ToggleScanControls()
        
        # update displayed hardware infos
        self.UpdateHardware()
        self.StartDeviceTimer()
        
        # refresh event list
        self.tree_events.RefreshEvents()
        #self.tree_events.Unfold(3) # unfold 3 levels of event tree
        self.tree_events.UnfoldSequence(0) # unfold 1st sequence
        
        # set current working directory
        os.chdir(user_path)
    
    def __create_widgets(self):
        """
        
            Fill in widgets
        
        """
        # history and filter list
        self.history = HistoryControl(self.panel)
        self.filter = FilterControl(self.panel)
        
        # event list + scan options
        self.tree_events = ScanEventList(self.panel)
        self.progress_bar = wx.StaticText(self.panel, -1, "0%",  style=wx.TE_CENTER)
        self.auto_update = wx.CheckBox(self.panel, -1, "Auto update during scan")
        
        # graph panel
        self.notebook = PlotNotebook(self.panel, -1)
        
        # bottom widgets
        self.CreateDeviceWidgets()
    
    def CreateDeviceWidgets(self):
        """
        
        Create widgets associated with loaded physical devices.
        Devices are either defined in the device configuration file or detected
        with the hardware.ScanHardware function.
        
        """
        # destroy existing widgets, if any
        if hasattr(self,'split_window'):
            if self.split_window!=None:
                sizer = self.split_window.Parent.GetSizer()
                if sizer!=None: # if the splitter window is in a sizer, replace with plot notebook
                    sizer.Replace(self.split_window,self.notebook)
                    self.notebook.Reparent(self.panel)
                self.split_window.Destroy()
        
        # create device widgets
        self.device_widgets = hardware.get_widgets(self.panel)
        if len(self.device_widgets)>0:
            # create splitter window and widget notebook
            self.split_window = Splitter(self.panel,-1,style=wx.SP_LIVE_UPDATE,proportion=0.85)
            self.nb_widgets = wx.Notebook(self.split_window,-1,style=0)
            # replace plot notebook with splitter window in containing sizer
            sizer = self.notebook.Parent.GetSizer()
            if sizer!=None:
                sizer.Replace(self.notebook,self.split_window)
            # place plot notebook in splitter window
            self.notebook.Reparent(self.split_window)
            self.split_window.SplitHorizontally(self.notebook,self.nb_widgets)
            self.split_window.SetMinimumPaneSize(100)
            # fill widget notebook
            for x in self.device_widgets:
                x.Reparent(self.nb_widgets)
                self.nb_widgets.AddPage(x,x.title)
        else:
            self.split_window = None
            self.nb_widgets = None
        # refresh interface
        if self.panel.GetSizer()!=None:
            self.panel.SetSizerAndFit(self.panel.GetSizer())
        
    def __create_event_bindings(self):
        """
        
        Bind events with appropriate handlers
        
        """
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        self.Bind(wx.EVT_CHECKBOX, self.SetRefresh)
        pub.subscribe(self.SetAxisFromPlot, "plot.move_axis")
        pub.subscribe(self.OnStartMeasurement, "scan.start")
        pub.subscribe(self.SetStatusText, "set_status_text")
        pub.subscribe(self.OnStopMeasurement, "scan.after")
        pub.subscribe(self.SetProgressValue, "progress_change")
        pub.subscribe(self.SetRefresh, "request_canvas")
        pub.subscribe(self.BroadcastWindow, "request_top_window")
    
    def __create_menu(self):
        """
        
        Create main menu
        
        """
        # File menu
        menuFile = wx.Menu()
        mitem = menuFile.Append(wx.NewId(), "&Open scan")
        self.Bind(wx.EVT_MENU, self.OnLoad, id=mitem.Id)
        menuFile.AppendSeparator()
        mitem = menuFile.Append(wx.NewId(), "&Settings")
        self.Bind(wx.EVT_MENU, self.OnSettings, id=mitem.Id)
        mitem = menuFile.Append(wx.NewId(), "&Default units")
        self.Bind(wx.EVT_MENU, self.OnDefaultUnits, id=mitem.Id)
        menuFile.AppendSeparator()
        mitem = menuFile.Append(wx.NewId(), "E&xit")
        self.Bind(wx.EVT_MENU, self.OnQuit, id=mitem.Id)
        
        # hardware menu
        menuHardware = wx.Menu()
        mitem = menuHardware.Append(wx.NewId(), "&Reset Current Devices")
        self.Bind(wx.EVT_MENU, self.OnResetHardware, id=mitem.Id)
        mitem = menuHardware.Append(wx.NewId(), "&Scan Hardware...")
        self.Bind(wx.EVT_MENU, self.OnScanHardware, id=mitem.Id)
        menuConfigMain = wx.Menu()
        self.menuConfigInput = wx.Menu()
        menuConfigMain.AppendSubMenu(self.menuConfigInput, "&Input Devices")
        self.menuConfigAxes = wx.Menu()
        menuConfigMain.AppendSubMenu(self.menuConfigAxes, "&Motion Devices")
        menuHardware.AppendSubMenu(menuConfigMain, "&Configure")        
        
        # help menu
        menuHelp = wx.Menu()
        mitem = menuHelp.Append(wx.NewId(), "&About TeraPy")
        self.Bind(wx.EVT_MENU, self.OnAbout, id=mitem.Id)
        mitem = menuHelp.Append(wx.NewId(), "&Online documentation")
        self.Bind(wx.EVT_MENU, self.OnOpenDoc, id=mitem.Id)
        
        self.menuBar = wx.MenuBar()
        self.menuBar.Append(menuFile, "&File")
        self.menuBar.Append(menuHardware, "Ha&rdware")
        self.menuBar.Append(menuHelp, "&Help")
        self.SetMenuBar(self.menuBar)
    
    def CreateHardwareConfigMenu(self):
        """
        
        Fill hardware menu with loaded devices and attach actions
        
        """
        # first check whether we should delete an old device list
        if(self.menuConfigInput.GetMenuItemCount() > 0):
            for mnu in self.menuConfigInput.GetMenuItems():
                self.menuConfigInput.Delete(mnu.GetId())
        if(self.menuConfigAxes.GetMenuItemCount() > 0):
            for mnu in self.menuConfigAxes.GetMenuItems():
                self.menuConfigAxes.Delete(mnu.GetId())
                
        # add devices to the list
        for dev in hardware.devices['input']:
            i = wx.NewId()
            self.menuConfigInput.Append(i, dev.ID + " " + dev.name)
            self.Bind(wx.EVT_MENU, self.OnConfigureInput, id=i)
        for dev in hardware.devices['axis']:
            i = wx.NewId()
            self.menuConfigAxes.Append(i, dev.ID + ", Axis:" + str(dev.axis) + " " + dev.name)
            self.Bind(wx.EVT_MENU, self.OnConfigureAxis, id=i)
        
    def __set_properties(self):
        """ 
        
        Set properties and layout
        
        """
        self.tree_events.SetMinSize((-1,600))
        self.notebook.SetMinSize((600,-1))
        
        self.progress_bar.SetForegroundColour(wx.Colour(0, 0, 0))
        self.progress_bar.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))            
        
        self.auto_update.SetValue(True)
        
        self.filter.Enable(False)
    
    def __do_layout(self):
        """
        
        Place widgets in main frame
        
        """
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # vertical sizer for scan history
        vbox0ast = wx.StaticBox(self.panel, -1, "Scan history")
        vbox0a = wx.StaticBoxSizer(vbox0ast, wx.VERTICAL)
        vbox0a.Add(self.history, 1, wx.EXPAND|wx.ALL, 2)
        
        vbox0bst = wx.StaticBox(self.panel, -1, "Post-processing")
        vbox0b = wx.StaticBoxSizer(vbox0bst, wx.VERTICAL)
        vbox0b.Add(self.filter, 1, wx.EXPAND|wx.ALL,0)
        
        vbox0 = wx.BoxSizer(wx.VERTICAL)
        vbox0.Add(vbox0a, 1, wx.EXPAND|wx.ALL, 2)
        vbox0.Add(vbox0b, 2, wx.EXPAND|wx.ALL, 2)
        
        # vertical sizers for time scan control
        vbox3st = wx.StaticBox(self.panel, -1, "Scan settings")
        vbox3 = wx.StaticBoxSizer(vbox3st, wx.VERTICAL)
        vbox3.Add(self.tree_events, 1, wx.EXPAND|wx.ALL, 0)
        
        # progress display
        hbox5st = wx.StaticBox(self.panel, -1, "Scan progress")
        hbox5 = wx.StaticBoxSizer(hbox5st, wx.HORIZONTAL)
        hbox5.AddStretchSpacer()
        hbox5.Add(self.progress_bar, 0, wx.ALIGN_CENTER_HORIZONTAL, 2)
        hbox5.AddStretchSpacer()
        
        # options
        vbox6st = wx.StaticBox(self.panel, -1, "Options")
        vbox6 = wx.StaticBoxSizer(vbox6st, wx.VERTICAL)
        vbox6.Add(self.auto_update, 1, wx.EXPAND|wx.ALL, 2)
        
        # top level sizers
        hbox0 = wx.BoxSizer(wx.HORIZONTAL)
        hbox0.Add(vbox0, 0, wx.EXPAND|wx.ALL, 2) # x|o|o
        if self.split_window !=None:
            hbox0.Add(self.split_window,1,wx.EXPAND) # o|x|o
        else:  
            hbox0.Add(self.notebook, 1, wx.EXPAND) # o|x|o
        vbox2 = wx.BoxSizer(wx.VERTICAL)
        vbox2.Add(vbox3, 0, wx.EXPAND|wx.ALL, 2)
        vbox2.Add(hbox5, 0, wx.EXPAND|wx.ALL, 2)
        vbox2.Add(vbox6, 0, wx.EXPAND|wx.ALL, 2)
        hbox0.Add(vbox2, 0, wx.EXPAND|wx.ALL, 2)# o|o|x
                
        # add sizers to main sizer
        main_sizer.Add(hbox0, 1, wx.EXPAND)
        
        # attach main sizer to panel to adjust element sizes
        self.panel.SetAutoLayout(True)
        self.panel.SetSizer(hbox0)
        hbox0.Fit(self.panel)
        hbox0.SetSizeHints(self.panel)
        
        self.Fit()
        self.Maximize()
    
    def SetStatusText(self, inst=None):
        """
        
            Set main window status bar text.
            Can be called directly or as a pubsub event subscriber.
            
            Parameters:
                inst    -    pubsub data
        
        """
        if isinstance(inst,str):
            wx.Frame.SetStatusText(self,inst)
        else:
            wx.Frame.SetStatusText(self,inst.data)
            
    def SetRefresh(self, inst):
        """
        
            Report on the state of the "automatic update" checkbox through pubsub.
            
            Parameters:
                inst    -    pubsub data
        
        """
        # needed to report auto update flag
        pub.sendMessage("broadcast_refresh",data=self.auto_update.GetValue())
    
    def OnStartMeasurement(self, event=None):
        """
        
            Actions preceding a new measurement.
            
            Parameters:
                event    -    event object (wx.Event)
        
        """
        meas = event.data
        # disable controls
        self.ToggleScanControls(False)
        # stop axis/input display update
        self.StopDeviceTimer()
        
        # add entries to scan history
        if len(meas.shape)==1:
            # only one measurement array
            meas.data[0].name = self.history.Insert(meas.data[0],meas.name)
            meas.data[0].xml = meas.xml # copy xml tree for easier access
        else:
            # more than one array
            for n in range(len(meas.shape)):
                meas.data[n].name = self.history.Insert(meas.data[n],meas.name + " " +str(n))
                meas.data[n].xml = meas.xml # copy xml tree for easier access
        
        # set status bar
        pub.sendMessage("set_status_text","Scan sequence \""+meas.name+"\" started at " + strftime("%H:%M:%S", localtime()))
        self.is_scanning = True
        
    
    def SetProgressValue(self, event):
        """
        
            Set progress bar value from pubsub event.
            
            Parameters:
                event    -    event object (wx.Event)
        
        """
        value = event.data
        if value < 0:
            value = 0
        if value > 100:
            value = 100
        self.progress_bar.SetLabel("%d%%" % value)

    def OnQuit(self, event = None):
        """
        
            Quit application.
            
            Parameters:
                event    -    event object (wx.Event)
        
        """
        self.Close(True)
        
    def OnCloseWindow(self, event):
        """
        
            Actions triggered when main window is closed.
            
            Parameters:
                event    -    event object (wx.Event)
        
        """
        self.StopDeviceTimer()
        # stop scan thread
        if not(self.is_scanning):
            pub.unsubAll()
            self.Destroy()
        else:
            if wx.MessageBox("Scan is running! Really quit?", "Quit", style=wx.YES | wx.NO) == wx.YES:
                pub.sendMessage("scan.stop")
                pub.unsubAll()
                wx.CallAfter(self.Destroy)
    
    def OnAbout(self, event):
        """
        
            About dialog.
            
            Parameters:
                event    -    event object (wx.Event)
        
        """
        dlg = wx.MessageDialog(self, "TeraPy (c) 2010-2013 D. Dietze, 2013-2014 V. Paeder\nVersion: " + __version__,caption="About",style=wx.OK,pos=wx.DefaultPosition)
        dlg.ShowModal()
        dlg.Destroy()
    
    def OnSettings(self, event):
        """
        
            Open settings dialog.
            
            Parameters:
                event    -    event object (wx.Event)
        
        """
        from terapy.core.settings import SettingsDialog
        dlg = SettingsDialog(self)
        dlg.ShowModal()
        dlg.Destroy()
        #dlg.ShowModal()
        #dlg.Destroy()

    def OnDefaultUnits(self, event):
        """
        
            Open default units dialog.
            
            Parameters:
                event    -    event object (wx.Event)
        
        """
        from terapy.core.axedit import AxesPropertiesDialog, AxisInfos, du
        labels = [AxisInfos(x[0],x[1]) for x in du.items()]
        dlg = AxesPropertiesDialog(self, "Default units", axlist=labels, read_only = [True, False], format = False)
        if dlg.ShowModal() == wx.ID_OK:
            for x in dlg.GetValue():
                du[x.name] = x.units
            pub.sendMessage("default_units.changed")
        dlg.Destroy()

    def OnResetHardware(self, event = None):
        """
        
            Trigger reset of loaded devices.
            This function is meant to be called from main menu.
            
            Parameters:
                event    -    event object (wx.Event)
        
        """
        if(wx.MessageBox("Are you sure?!", "Reset Hardware", style=wx.YES | wx.NO) != wx.YES):
            return
    
        # stop timers
        self.StopDeviceTimer()
        
        print "reset..."
        for x in hardware.devices['axis']:
            print "reset", x.name
            x.reset()        
        for x in hardware.devices['input']:
            print "reset", x.name
            x.reset()        
        
        # restart timers
        self.StartDeviceTimer()
            
    def OnLoad(self, event = None):
        """
        
            Announce through pubsub that a load event has been called.
            This function doesn't implement a load file routine.
            It only announces a load request, which should be handled elsewhere (e.g. history control).
            
            Parameters:
                event    -    event object (wx.Event)
        
        """
        pub.sendMessage("load_data")
                    
    def ToggleScanControls(self, state = True):
        """
        
            Enable/Disable interface elements.
            
            Parameters:
                state    -    state (bool)
        
        """
        # enable menus
        self.menuBar.EnableTop(0, state)
        self.menuBar.EnableTop(1, state)
        # enable widgets
        for x in self.device_widgets:
            x.Enable(state)
        
    def OnStopMeasurement(self, event = None):
        """
        
            Actions following the end of a measurement.
            
            Parameters:
                event    -    event object (wx.Event)
        
        """
        meas = event.data
        # swap buttons' status
        self.ToggleScanControls(True)
        
        # status bar
        pub.sendMessage("set_status_text","Scan finished")
        
        # update plots
        for x in meas.data:
            if x.plot!=None:
                x.plot.Recompute()
        
        # restart input signal and axis position timers
        self.StartDeviceTimer()
        self.is_scanning = False
    
    def SetAxisFromPlot(self, event):
        """
        
            Set currently selected axis device to given position.
            This function is meant to be called by pubsub.
            
            Parameters:
                event    -    event object (wx.Event)
        
        """
        # set selected stage position
        if hasattr(self,'nb_widgets'):
            if self.nb_widgets!=None:
                curwg = self.nb_widgets.CurrentPage
                if hasattr(curwg,'axis'):
                    curwg.SetValue(event.data)
        
    def UpdateHardware(self):
        """
        
        Actions following a change in the list of loaded hardware devices
        
        """
        self.CreateHardwareConfigMenu()
    
    def OnScanHardware(self, event):
        """
        
            Trigger scan for connected devices.
            This function is meant to be called from main menu.
            
            Parameters:
                event    -    event object (wx.Event)
        
        """
        if(wx.MessageBox("Are you sure? This will reset all hardware settings!", "Scan for Hardware", style=wx.YES | wx.NO) != wx.YES):
            return
    
        # stop input signal timer
        self.StopDeviceTimer()
        
        # scan hardware
        hardware.scan_hardware()
        hardware.store_hardware_info()
        hardware.initiate_hardware()    # boot devices
        
        # create overview
        devlist = ""
        for dev in hardware.devices['input']:
            devlist = devlist + dev.ID + ": " + dev.name + "\n"
        for dev in hardware.devices['axis']:
            devlist = devlist + dev.ID + "_" + str(dev.axis) + ": " + dev.name + "\n"
            
        # display overview
        dlg = wx.MessageDialog(self, devlist,caption="Found Hardware",style=wx.OK,pos=wx.DefaultPosition)
        dlg.ShowModal()
        dlg.Destroy()
        
        # update select boxes
        self.UpdateHardware()
        self.CreateDeviceWidgets()
        
        # restart device timer
        self.StartDeviceTimer()
    
    def OnConfigureInput(self, event):
        """
        
            Call configure function of selected input device.
            Menu action.
            
            Parameters:
                event    -    event object (wx.Event)
        
        """
        mId = GetItemIds(event.GetEventObject()).index(event.GetId())
        self.StopDeviceTimer()                        # stop signal refresh        
        hardware.devices["input"][mId].configure()
        hardware.store_hardware_info()
        self.StartDeviceTimer()                        # restart signal refresh
        
    def OnConfigureAxis(self, event):
        """
        
            Call configure function of selected axis device.
            Menu action.
            
            Parameters:
                event    -    event object (wx.Event)
        
        """
        mId = GetItemIds(event.GetEventObject()).index(event.GetId())
        self.StopDeviceTimer()                        # stop signal refresh        
        hardware.devices["axis"][mId].configure()
        hardware.store_hardware_info()
        self.StartDeviceTimer()                        # restart signal refresh
    
    def OnOpenDoc(self, event=None):
        """
        
            Open documentation in web browser.
        
        """
        import webbrowser
        webbrowser.open(__doc_url__)
    
    def StartDeviceTimer(self):
        """
        
        Start update timers for loaded devices
        
        """
        for x in self.device_widgets:
            x.timer.Start(250)
        
    def StopDeviceTimer(self):
        """
        
        Stop update timers for loaded devices
        
        """
        for x in self.device_widgets:
            x.timer.Stop()
    
    def BroadcastWindow(self, inst=None):
        """
        
            Send main window reference through pubsub.
            
            Parameters:
                inst    -    pubsub event data (not used, but function normally called by pubsub)
        
        """
        pub.sendMessage("broadcast_window", data=self)

# launch application
if __name__ == '__main__':
    app = wx.App(redirect=False)
    frame = TeraPyMainFrame()
    frame.Show(True)
    #import wx.lib.inspection
    #wx.lib.inspection.InspectionTool().Show()
    app.MainLoop()