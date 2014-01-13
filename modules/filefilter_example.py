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

    File filter class example

"""

from terapy.files.base import FileFilter

class FileFilterExample(FileFilter):
    """
    
        File filter class example
    
    """
    def __init__(self):
        FileFilter.__init__(self)
        self.ext = ["*.*"] # list of file extensions handled by this filter (list of str) 
        self.desc = "Example files" # name of file type (str)
        self.can_save = True # if True, this filter can be used to save data
        self.can_read = True # if True, this filter can be used to load data
        self.multi_data = False # if True, this filter can save multiple datasets in one file 
    
    def read(self,fname):
        """
        
            Read given file name.
            
            Parameters:
                fname    -    file name (str)
            
            Output:
                list of data (list of DataArray)
        
        """
        # Insert here what the filter should do to read a file
        return []

    def save(self, fname, data):
        """
        
            Save data to given file name.
            
            Parameters:
                fname    -    file name (str)
                data     -    data (DataArray)
        
        """
        # Insert here what the filter should do to save some data to a file
        return True
    