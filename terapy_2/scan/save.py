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

    Save scan event base class

"""

from terapy.scan.base import ScanEvent
import wx
import os
from terapy.core import icon_path, default_path
from time import strftime, localtime

class SaveBase(ScanEvent):
    """
    
        Save scan event base class
    
    """
    __extname__ = "SaveBase"
    def __init__(self, parent = None):
        ScanEvent.__init__(self, parent)
        self.filename = ""
        self.autoname = True
        self.propNames = ["File name","Automatic"]
        self.is_save = True
        self.is_visible = False
        self.config = ["filename","autoname"]
        self.filter = None
        
    def run(self, data):
        pass
    
    def refresh(self):
        ScanEvent.refresh(self)
        if self.autoname: self.filename=""
        if hasattr(self,'fname'): del self.fname
    
    def set(self, parent=None):
        dlg = FileSelectionDialog(parent, fname=self.filename, wildcard=self.get_wildcard(), autoname=self.autoname)
        if dlg.ShowModal() == wx.ID_OK:
            self.filename,self.autoname = dlg.GetValue()
            dlg.Destroy()
            return True
        else:
            dlg.Destroy()
            return False
    
    def populate(self):
        self.propNodes = [os.path.basename(self.filename),["No","Yes"][self.autoname]]
        self.create_property_root()
        self.set_property_nodes(True)
        
    def edit_label(self, event, pos):
        if pos==0:
            event.Veto()
            dlg = wx.FileDialog(self.host, "Choose output file", os.getcwd(), self.filename, self.get_wildcard() + "|All files (*.*)|*.*", wx.SAVE)
            if dlg.ShowModal()==wx.ID_OK:
                self.filename = dlg.GetPath()
                self.autoname = False
            dlg.Destroy()
        elif pos==1:
            event.Veto()
            self.autoname = not(self.autoname)
        
        self.refresh()
                
        self.propNodes = [os.path.basename(self.filename),["No","Yes"][self.autoname]]
        self.set_property_nodes(True)

    def get_wildcard(self):
        if self.filter!=None:
            wc = self.filter.desc + " ("
            for x in self.filter.ext:
                wc += x + ","
            wc = wc[:-1] + ")|"
            for x in self.filter.ext:
                wc += x + ";"
            return wc[:-1]
        else:
            return ""
    
    def make_filename(self):
        # create temporary 'fname' variable to store name during measurement (will be wiped with self.refresh())
        if not(hasattr(self,'fname')):
            if self.autoname:
                # get correct extension
                if self.filter!=None:
                    ext = self.filter.ext[0][1:]
                else:
                    ext = ".dat"
                fname = "scan_" + strftime("%d-%m-%Y_%H-%M-%S", localtime()) + ext
                pathname = os.path.join(default_path, strftime("%Y-%m-%d", localtime()))
            else:
                fname = os.path.basename(self.filename)
                pathname = os.path.join(os.path.dirname(self.filename), strftime("%Y-%m-%d", localtime()))
            
            if not os.path.exists(pathname):
                os.makedirs(pathname)
            self.fname = os.path.join(pathname, fname)
        
        return self.fname
    
    def get_icon(self):
        return wx.Image(icon_path + "event-save.png").ConvertToBitmap()

class FileSelectionDialog(wx.Dialog):
    """
    
        Save scan event configuration dialog
    
    """
    def __init__(self, parent = None, title="Select output file", fname = "", wildcard = "", autoname = True):
        """
        
            Initialization.
            
            Parameters:
                parent    -    parent window (wx.Window)
                title     -    dialog title (str)
                fname     -    default file name (str)
                wildcard  -    wildcards (str)
                autoname  -    if True, set name automatically
        
        """
        wx.Dialog.__init__(self, parent, title=title)
        self.label_filename = wx.StaticText(self, -1, "File name")
        self.input_filename = wx.TextCtrl(self, -1, os.path.basename(fname))
        self.button_filename = wx.Button(self,-1,"...")
        self.check_autoname = wx.CheckBox(self,-1,"Name with time stamp")

        self.button_OK = wx.Button(self, wx.ID_OK)
        self.button_Cancel = wx.Button(self, wx.ID_CANCEL)
        
        self.input_filename.SetMinSize((300,-1))
        
        hboxf = wx.BoxSizer(wx.HORIZONTAL)
        hboxf.Add(self.input_filename, 0, wx.ALL|wx.EXPAND, 2)
        hboxf.Add(self.button_filename, 0)
        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.AddStretchSpacer(1)
        hbox.Add(self.button_Cancel, 0, wx.RIGHT|wx.ALIGN_RIGHT, 5)
        hbox.Add(self.button_OK, 0, wx.RIGHT|wx.ALIGN_RIGHT, 5)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.label_filename, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(hboxf, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.check_autoname, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(hbox, 0, wx.ALL|wx.EXPAND, 2)
        self.SetSizer(sizer)
        self.Fit()
        self.label_filename.Enable(not(autoname))
        self.input_filename.Enable(not(autoname))
        self.button_filename.Enable(not(autoname))
        self.check_autoname.SetValue(autoname)
        
        self.Bind(wx.EVT_CHECKBOX, self.OnAutonameCheck, self.check_autoname)
        self.Bind(wx.EVT_BUTTON, self.OnFilenameButton, self.button_filename)
        self.input_filename.Bind(wx.EVT_SET_FOCUS, self.OnSetFocus, self.input_filename)
        self.input_filename.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus, self.input_filename)
        self.fname = fname
        self.wc = wildcard
    
    def OnAutonameCheck(self, event = None):
        """
        
            Actions following ticking autoname checkbox.
            
            Parameters:
                event    -    wx.Event
        
        """
        autoname = self.check_autoname.GetValue()
        self.label_filename.Enable(not(autoname))
        self.input_filename.Enable(not(autoname))
        self.button_filename.Enable(not(autoname))
        
    def OnSetFocus(self, event=None):
        """
        
            Actions on file name text box focusing.
            
            Parameters:
                event    -    wx.Event
        
        """
        self.input_filename.SetValue(self.fname)
    
    def OnKillFocus(self, event=None):
        """
        
            Actions after file name text box loses focus.
            
            Parameters:
                event    -    wx.Event
        
        """
        path = self.input_filename.GetValue()
        if os.path.isfile(path):
            self.fname = path
        self.input_filename.SetValue(os.path.basename(self.fname))

    def OnFilenameButton(self, event = None):
        """
        
            Actions triggered by "..." button press.
            
            Parameters:
                event    -    wx.Event
        
        """
        dlg = wx.FileDialog(self, "Choose output file", os.getcwd(),"", self.wc + "|All files (*.*)|*.*", wx.SAVE)
        if dlg.ShowModal()==wx.ID_OK:
            self.input_filename.SetValue(dlg.GetFilename())
            self.fname = dlg.GetPath()
        dlg.Destroy()
    
    def GetValue(self):
        """
        
            Return dialog values.
            
            Output:
                file name (str), auto name (bool)
        
        """
        return self.fname, self.check_autoname.GetValue()
