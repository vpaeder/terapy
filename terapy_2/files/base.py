#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2013  Vincent Paeder
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

    Generic file filter class

"""

import os
class FileFilter():
    """
    
        Generic file filter class
    
    """
    def __init__(self):
        self.ext = ["*.*"]
        self.desc = "Files"
        self.can_save = True
        self.can_read = True
        self.multi_data = False
    
    def read(self,fname):
        """
        
            Read given file name.
            
            Parameters:
                fname    -    file name (str)
            
            Output:
                data (DataArray)
        
        """
        return []

    def save(self, fname, data):
        """
        
            Save data to given file name.
            
            Parameters:
                fname    -    file name (str)
                data     -    data (DataArray)
        
        """
        return True
    
    def wildcard(self):
        """
        
            Return wildcards associated with filter.
            
            Output:
                list of wildcards (list of str)
        
        """
        wc = self.desc + " ("
        for x in self.ext:
            wc = wc + x + ", "
        wc = wc[:-2] +")|"
        for x in self.ext:
            wc = wc + x + ";"
        return wc[:-1]

    def strip(self,fname):
        """
        
            Strip file name of extension.
            
            Parameters:
                fname    -    file name (str)
            
            Output:
                stripped file name (str)
        
        """
        tname = os.path.basename(fname)
        tname = tname.split(".")
        tname[-1] = ""
        tname = ".".join(tname)
        return tname
