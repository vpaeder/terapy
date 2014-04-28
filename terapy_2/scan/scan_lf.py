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

    List scan from file event class

"""

from terapy.scan.scan_s import Scan
import wx
from numpy import array
from time import sleep
import os

class Scan_LF(Scan):
    """
    
        List scan from file event class

        Scan given axis device following list of values taken from given file.
    
    """
    __extname__ = "List scan from file"
    def __init__(self, parent = None):
        Scan.__init__(self, parent)
        self.axis = 0
        self.N = 1
        self.list = [0.0]
        self.fname = ""
        self.propNames = ["Axis","File"]
        self.config = ["axis","fname","N"]
        self.parse_list()
    
    def refresh(self):
        Scan.refresh(self)
        self.N = len(self.list)
        
    def run(self, data):
        self.itmList = self.get_children()
        ax = self.axlist[self.axis]
        ax.prepareScan()
        # scan selected axis from min to max
        coords = array(self.list)
        n=-1
        while self.can_run and n<self.N-1:
            n+=1
            ax.goTo(coords[n])
            while (ax.get_motion_status() != 0 and self.can_run):
                sleep(0.01)
            data.SetCoordinateValue(self.m_ids, ax.pos()) # read axis position
            self.run_children(data)
            data.Increment(self.m_ids)
        data.Decrement(self.m_ids)
        data.DecrementScanDimension(self.m_ids)
        return True

    def set(self, parent=None):
        self.refresh()
        dlg = ListFileSelectionDialog(parent, axlist=[x.name for x in self.axlist], axis=self.axis, fname=self.fname)
        if dlg.ShowModal() == wx.ID_OK:
            self.axis, self.fname = dlg.GetValue()
            self.parse_list()
            dlg.Destroy()
            return True
        else:
            dlg.Destroy()
            return False
        self.set_property_nodes(True)

    def populate(self):
        try:
            self.propNodes = [self.axlist[self.axis].name, os.path.basename(self.fname)]
        except:
            self.propNodes = ["", os.path.basename(self.fname)]
        self.create_property_root()
        self.set_property_nodes(True)

    def set_property(self, pos, val):
        try:
            if pos==0:
                self.axis = int(val)
        except:
            pass
        self.propNodes = [self.axlist[self.axis].name, os.path.basename(self.fname)]
        self.set_property_nodes()
    
    def edit_label(self, event, pos):
        Scan.edit_label(self, event, pos)
        if pos==1:
            event.Veto()
            dlg = wx.FileDialog(self.host, "Choose input file", os.getcwd(), self.fname, "Data files (*.dat,*.csv,*.txt)|*.dat;*.csv;*.txt|All files (*.*)|*.*", wx.OPEN)
            if dlg.ShowModal()==wx.ID_OK:
                self.fname = dlg.GetPath()
                self.parse_list()
                self.autoname = False
            dlg.Destroy()
            self.propNodes[1] = os.path.basename(self.fname)
            self.set_property_nodes()
            
    def parse_list(self):
        self.list = []
        try:
            f = open(self.fname,'r')
            s = f.read().replace('\r\n','\n').replace('\r','\n')
            s = s.split('\n')
            self.list = map(float,s)
        except:
            pass
        self.N = len(self.list)

class ListFileSelectionDialog(wx.Dialog):
    """
    
        List scan from file configuration dialog
    
    """
    def __init__(self, parent = None, title="Select output file", axlist=[], axis=0, fname=""):
        """
        
            Initialization.
            
            Parameters:
                parent    -    parent window (wx.Window)
                title     -    dialog title (str)
                axlist    -    list of axis devices (list of str)
                axis      -    default selection (int)
                fname     -    default file name (str)
        
        """
        wx.Dialog.__init__(self, parent, title=title)
        self.label_axis = wx.StaticText(self, -1, "Axis")
        self.choice_axis = wx.Choice(self, -1, choices=axlist)
        self.label_filename = wx.StaticText(self, -1, "File name")
        self.input_filename = wx.TextCtrl(self, -1, os.path.basename(fname))
        self.button_filename = wx.Button(self,-1,"...")
        self.input_filename.SetMinSize((300,-1))
        
        self.button_OK = wx.Button(self, wx.ID_OK)
        self.button_Cancel = wx.Button(self, wx.ID_CANCEL)
        
        hboxf = wx.BoxSizer(wx.HORIZONTAL)
        hboxf.Add(self.input_filename, 0, wx.ALL|wx.EXPAND, 2)
        hboxf.Add(self.button_filename, 0)
        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.AddStretchSpacer(1)
        hbox.Add(self.button_Cancel, 0, wx.RIGHT|wx.ALIGN_RIGHT, 5)
        hbox.Add(self.button_OK, 0, wx.RIGHT|wx.ALIGN_RIGHT, 5)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.label_axis, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.choice_axis, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.label_filename, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(hboxf, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(hbox, 0, wx.ALL|wx.EXPAND, 2)
        self.SetSizer(sizer)
        self.Fit()
        self.choice_axis.SetSelection(axis)
        self.input_filename.Bind(wx.EVT_SET_FOCUS, self.onSetFocus, self.input_filename)
        self.input_filename.Bind(wx.EVT_KILL_FOCUS, self.onKillFocus, self.input_filename)
        self.Bind(wx.EVT_BUTTON, self.onFilenameButton, self.button_filename)
        self.fname = fname
    
    def onSetFocus(self, event=None):
        """
        
            Actions on file name text box focusing.
            
            Parameters:
                event    -    wx.Event
        
        """
        self.input_filename.SetValue(self.fname)
    
    def onKillFocus(self, event=None):
        """
        
            Actions after file name text box loses focus.
            
            Parameters:
                event    -    wx.Event
        
        """
        path = self.input_filename.GetValue()
        if os.path.isfile(path):
            self.fname = path
        self.input_filename.SetValue(os.path.basename(self.fname))

    def onFilenameButton(self, event = None):
        """
        
            Actions triggered by "..." button press.
            
            Parameters:
                event    -    wx.Event
        
        """
        dlg = wx.FileDialog(self, "Choose input file", os.getcwd(),"", "Data files (*.dat,*.csv,*.txt)|*.dat;*.csv;*.txt|All files (*.*)|*.*", wx.OPEN)
        if dlg.ShowModal()==wx.ID_OK:
            self.input_filename.SetValue(os.path.basename(dlg.GetFilename()))
            self.fname = dlg.GetPath()
        dlg.Destroy()
    
    def GetValue(self):
        """
        
            Return dialog values.
            
            Output:
                index of selected device (int), file name (str)
        
        """
        return self.choice_axis.GetSelection(), self.fname
