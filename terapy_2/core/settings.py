#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2014  Vincent Paeder
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

    Main settings dialog

"""

import wx.grid
from wx.lib import sheet
from terapy.core.validator import PositiveFloatValidator

settings = {'default_path':['Backup folder','f'],'user_path':['User folder','f'],'config_path':['Configuration folder','f'],'filter_path':['Filter bank folder','f'],'module_path':['Module folder','f'],'refresh_delay':['Refresh delay','n']}

class SettingsDialog(wx.Dialog):
    """
    
        Main settings dialog
    
    """
    def __init__(self, parent = None, title="Main settings"):
        """
        
            Initialization.
            
            Parameters:
                parent    -    parent window (wx.Window)
                title     -    dialog title (str)
        
        """
        wx.Dialog.__init__(self, parent, title=title, size=(400,-1))
        self.sheet = sheet.CSheet(self)
        self.button_OK = wx.Button(self, wx.ID_OK)
        self.button_Cancel = wx.Button(self, wx.ID_CANCEL)
        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.AddStretchSpacer(1)
        hbox.Add(self.button_Cancel, 0, wx.RIGHT|wx.ALIGN_RIGHT, 5)
        hbox.Add(self.button_OK, 0, wx.RIGHT|wx.ALIGN_RIGHT, 5)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.sheet, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(hbox, 0, wx.ALL|wx.EXPAND, 2)
        self.SetSizerAndFit(sizer)
                
        # build list of settings
        self.slist = {}
        for x in settings:
            self.slist[x] = [settings[x][0], getattr(__import__('terapy.core', fromlist=[x]), x), settings[x][1]]
        
        # fill sheet
        self.sheet.SetSelectionMode(0)
        self.table = SettingsList(self.slist)
        self.sheet.SetTable(self.table)
        self.sheet.SetMaxSize((-1,300))
        self.sheet.SetMinSize((-1,300))
        self.sheet.AutoSizeColumn(0)
        self.sheet.SetColSize(1,300)
        
        # assign combo editor to 2nd column
        for x in self.slist:
            n = self.slist.keys().index(x)
            self.sheet.SetReadOnly(n,0,True)
            if self.slist[x][2] == 'n':
                self.sheet.SetCellEditor(n,1,wx.grid.GridCellFloatEditor(precision=1))
                self.sheet.SetCellAlignment(n,1,wx.ALIGN_RIGHT, wx.ALIGN_CENTRE)
            elif self.slist[x][2] == 'f':
                self.sheet.SetCellAlignment(n,1,wx.ALIGN_RIGHT, wx.ALIGN_CENTRE)
        
        self.Fit()
        self.Bind(wx.grid.EVT_GRID_EDITOR_CREATED, self.OnEditorShown)
        self.Bind(wx.grid.EVT_GRID_EDITOR_SHOWN, self.OnEditorShown)
        self.Bind(wx.grid.EVT_GRID_EDITOR_HIDDEN, self.OnEditorHidden)
        self.button_OK.Bind(wx.EVT_BUTTON, self.OnOk)

    def OnEditorShown(self, event=None):
        """
        
            Actions preceding editing a cell.
            
            Parameters:
                event    -    wx.Event
        
        """
        x = self.slist.keys()[event.Row]
        if self.slist[x][2]=='n':
            editor = self.sheet.GetCellEditor(event.Row,event.Col)
            control = editor.GetControl()
            if control!=None:
                control.SetValidator(PositiveFloatValidator())
                control.SetValue(self.table.GetValue(event.Row, event.Col))
            event.Skip()
        else:
            event.Veto()
            name = self.slist[x][0]
            dlg = wx.DirDialog(self,"Choose "+name)
            if dlg.ShowModal() == wx.ID_OK:
                self.slist[x][1] = dlg.GetPath()
    
    def OnEditorHidden(self, event=None):
        """
        
            Actions after editing a cell is over.
            
            Parameters:
                event    -    wx.Event
        
        """
        editor = self.sheet.GetCellEditor(event.Row,event.Col)
        control = editor.GetControl()
        x = self.slist.keys()[event.Row]
        if self.slist[x][2]=='n':
            try:
                self.table.SetValue(event.Row, event.Col, float(control.GetValue()))
                control.SetValue(str(float(control.GetValue())))
            except:
                control.SetValue("0.0")
                self.table.SetValue(event.Row, event.Col, 0.0)
        else:
            event.Skip()
    
    def OnOk(self, event=None):
        """
        
            Events preceding dialog destruction.
            
            Parameters:
                event    -    wx.Event
        
        """
        self.sheet.SaveEditControlValue()
        self.sheet.HideCellEditControl()
        # store settings
        import terapy.core
        for x in settings:
            setattr(terapy.core, x, self.slist[x][1])
        
        # propose to save to disk
        from terapy.core import main_config_file, root_path
        import os
        if main_config_file==None:
            main_config_file = os.path.join(root_path,"terapy.ini")
        if wx.MessageBox("Save to configuration file?", "Save settings", style=wx.YES | wx.NO) == wx.YES:
            self.SaveSettings(main_config_file)
        event.Skip()

    def SaveSettings(self, fname):
        """
        
            Save main settings to the file defined in terapy.core
            By default: <root directory>/terapy.ini
            Or: <config directory>/terapy.ini
        
        """
        from xml.dom import minidom
        from terapy.core.axedit import du
        
        doc = minidom.Document()
        croot = doc.createElement("config")
        croot.attributes["scope"] = "terapy"
        doc.appendChild(croot)
        for x in settings:
            root = doc.createElement(x)
            root.attributes["value"] = str(self.slist[x][1])
            croot.appendChild(root)
        for x in du:
            root = doc.createElement("units")
            root.attributes["type"] = x
            root.attributes["symbol"] = "{:~}".format(du[x].units)
            croot.appendChild(root)
        
        f = open(fname,'w')
        doc.writexml(f,indent="  ", addindent="  ", newl="\n")
        f.close()

class SettingsList(wx.grid.PyGridTableBase):
    """
    
        Table base class for settings
    
    """
    def __init__(self, data=[]):
        
        """
        
            Initialization.
            
            Parameters:
                data     -    dict of settings as (name (str), value, type ['f','n'])  
        
        """
        wx.grid.PyGridTableBase.__init__(self)
        self._cols = ["Setting","Value"]
        self.data = data
    
    def GetColLabelValue(self, col):
        """
        
            Return column label for given index.
            
            Parameters:
                col    -    column index (int)
            
            Output:
                column label (str)
        
        """
        return self._cols[col]

    def GetNumberRows(self):
        """
        
            Return number of rows.
            
            Output:
                number of rows (int)
        
        """
        return len(self.data.values())

    def GetNumberCols(self):
        """
        
            Return number of columns.
            
            Output:
                number of columns (int)
        
        """
        return len(self._cols)
    
    def GetValue(self, row, col):
        """
        
            Return value for given row and column index.
            
            Parameters:
                row    -    row index (int)
                col    -    column index (int)
            
            Output:
                value (float)
        
        """
        x = self.data.keys()[row]
        
        if self.data[x][2] == 'n' or col==0: 
            return str(self.data[x][col])
        elif self.data[x][2] == 'f':
            # compute optimal size
            sheet = self.GetView()
            dc = wx.WindowDC(sheet)
            sz = sheet.GetColSize(1)
            dc.SetFont(sheet.GetFont())
            txt = self.data[x][1]
            for n in range(len(txt)-1,-1,-1):
                w = dc.GetTextExtent("... " + txt[n:])
                if w[0]>sz: break
            
            if w[0]<=sz or (w[0]>sz and n==len(txt)-1):
                return txt
            else:
                return "... " + txt[n+2:]
    
    def SetValue(self, row, col, val):
        """
        
            Set value of given row and column index.
            
            Parameters:
                row    -    row index (int)
                col    -    column index (int)
                value  -    value (float)
        
        """
        x = self.data.keys()[row]
        self.data[x][col] = val
