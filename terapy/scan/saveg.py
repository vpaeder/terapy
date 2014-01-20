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
from terapy.core.choice import ChoicePopup
from time import strftime, localtime

class Save(ScanEvent):
    """
    
        Save scan event base class
    
    """
    __extname__ = "Save"
    def __init__(self, parent = None):
        ScanEvent.__init__(self, parent)
        self.filename = ""
        self.fclass = ""
        self.autoname = True
        self.propNames = ["File format","File name","Automatic"]
        self.is_save = True
        self.config = ["fclass","filename","autoname"]
        self.filter = None
        
    def run(self, data):
        fname = self.make_filename()
        for n in range(self.m_id+1): # save what has been measured before calling 'save'
            data.data[n].filename = fname
            self.filter.save(fname, data.data[n],name="M_"+str(n))
    
    def refresh(self):
        ScanEvent.refresh(self)
        from terapy import files
        if self.autoname: self.filename=""
        if hasattr(self,'fname'): del self.fname
        modnames = [x.__name__ for x in files.modules if x().can_save]
        if modnames.count(self.fclass)==0:
            self.fclass = modnames[0]
        self.filter = files.modules[modnames.index(self.fclass)]()
    
    def set(self, parent=None):
        dlg = FileFilterSelectionDialog(parent, fname=self.filename, fclass=self.fclass, autoname=self.autoname)
        if dlg.ShowModal() == wx.ID_OK:
            self.fclass,self.filename,self.autoname = dlg.GetValue()
            dlg.Destroy()
            return True
        else:
            dlg.Destroy()
            return False
    
    def populate(self):
        self.propNodes = [self.fclass,os.path.basename(self.filename),["No","Yes"][self.autoname]]
        self.create_property_root()
        self.set_property_nodes(True)
        
    def edit_label(self, event, pos):
        from terapy import files
        if pos==0:
            br = self.host.GetBoundingRect(self.get_property_node(0))
            w = ChoicePopup(self.host,-1,choices=[x().desc + " (" + ", ".join(x().ext) + ")" for x in files.modules if x().can_save],pos=br.GetPosition(), size=br.GetSize(), style=wx.CB_DROPDOWN|wx.CB_READONLY)
            w.SetSelection([x.__name__ for x in files.modules if x().can_save].index(self.fclass))
            w.Bind(wx.EVT_CHOICE,self.onSelectFilter)
            w.SetFocus()
            if wx.Platform == '__WXMSW__':
                w.Bind(wx.EVT_KILL_FOCUS,self.onSelectFilter)
        elif pos==1:
            event.Veto()
            dlg = wx.FileDialog(self.host, "Choose output file", os.getcwd(), self.filename, files.save_wildcards(allfiles=False), wx.SAVE)
            if dlg.ShowModal()==wx.ID_OK:
                self.filename = dlg.GetPath()
                self.autoname = False
                self.filter = files.modules[dlg.GetFilterIndex()]()
                self.fclass = self.filter.__class__.__name__
            dlg.Destroy()
        elif pos==2:
            event.Veto()
            self.autoname = not(self.autoname)
        
        self.refresh()
                
        self.propNodes = [self.fclass,os.path.basename(self.filename),["No","Yes"][self.autoname]]
        self.set_property_nodes(True)

    def onSelectFilter(self, event=None):
        from terapy import files
        mods = [x for x in files.modules if x().can_save]
        self.filter = mods[event.GetEventObject().GetSelection()]()
        self.fclass = self.filter.__class__.__name__
        self.propNodes[0] = self.fclass
        # change file extension
        fpath = list(os.path.splitext(self.filename))
        if len(fpath)>1:
            fpath[-1] = self.filter.ext[0][2:]
            if fpath[0]=="": fpath[0]="default"
            self.filename = ".".join(fpath)
        
        if self.autoname:
            self.filename = ""
        self.propNodes[1] = os.path.basename(self.filename)
        
        self.set_property_nodes()
        # notify tree that editing is finished
        evt = wx.TreeEvent(wx.wxEVT_COMMAND_TREE_END_LABEL_EDIT,self.host.GetId())
        evt.SetItem(self.host.GetSelection())
        self.host.GetEventHandler().ProcessEvent(evt)

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

class FileFilterSelectionDialog(wx.Dialog):
    """
    
        Save scan event configuration dialog
    
    """
    def __init__(self, parent = None, title="Select output file", fname = "", fclass = "", autoname = True):
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
        from terapy import files
        descs = [x().desc + " (" + ", ".join(x().ext) + ")" for x in files.modules if x().can_save]
        self.mods = [x for x in files.modules if x().can_save]
         
        self.label_modules = wx.StaticText(self, -1, "File type")
        self.choice_modules = wx.Choice(self, -1, choices=descs)
        self.label_filename = wx.StaticText(self, -1, "File name")
        self.input_filename = wx.TextCtrl(self, -1, os.path.basename(fname))
        self.button_filename = wx.Button(self,-1,"...")
        self.check_autoname = wx.CheckBox(self,-1,"Name with time stamp")
        
        self.fclass = fclass
        if [x.__name__ for x in self.mods].count(fclass):
            self.choice_modules.SetSelection([x.__name__ for x in self.mods].index(fclass))

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
        sizer.Add(self.label_modules, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.choice_modules, 0, wx.ALL|wx.EXPAND, 2)
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
        self.Bind(wx.EVT_CHOICE, self.OnTypeChange, self.choice_modules)
        self.fname = fname
    
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
        from terapy import files
        dlg = wx.FileDialog(self, "Choose output file", os.getcwd(),"", files.save_wildcards(allfiles=False), wx.SAVE)
        dlg.SetFilterIndex(self.choice_modules.GetPosition())
        if dlg.ShowModal()==wx.ID_OK:
            self.input_filename.SetValue(dlg.GetFilename())
            self.fname = dlg.GetPath()
            self.choice_modules.SetPosition(dlg.GetFilterIndex())
        dlg.Destroy()
    
    def OnTypeChange(self, event = None):
        fpath = list(os.path.splitext(self.fname))
        if len(fpath)>1:
            fpath[-1] = self.mods[event.GetSelection()]().ext[0][2:]
            if fpath[0]=="": fpath[0]="default"
            self.fname = ".".join(fpath)
            self.input_filename.SetValue(os.path.basename(self.fname))
        if self.check_autoname.GetValue(): self.fname = ""
    
    def GetValue(self):
        """
        
            Return dialog values.
            
            Output:
                file name (str), auto name (bool)
        
        """
        return self.mods[self.choice_modules.GetCurrentSelection()].__name__, self.fname, self.check_autoname.GetValue()
