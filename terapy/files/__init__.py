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

    File parsing functions
    
    Properties:
        modules    -    list of available file filters
    
    Each parsing method must be implemented as a FileFilter class (see base.py).
    FileFilter classes contained in Python scripts within this folder will be
    automatically recognized and added to file filter list. 

"""

from terapy.files.base import FileFilter
# import file filter classes
import os

from terapy.core import check_py

# import file filter classes
curdir = os.path.dirname(__file__)
from terapy.core import parse_modules
modules = parse_modules(__package__, curdir, FileFilter)
    
# search for custom modules
from terapy.core import module_path
if os.path.exists(module_path):
    modules.extend(parse_modules("custom.file.", module_path, FileFilter))

def wildcards(allfiles=True):
    """
    
        Build a list of wildcards associated with available file filters.
        
        Parameters:
            allfiles    -    if True, add generic "All files (*.*)" entry to list
        
        Output:
            wildcard list (list)
    
    """
    wc = ""
    for x in modules:
        wc = wc + x().wildcard() + "|"
    
    if allfiles:
        return wc + "All files (*.*)|*.*"
    else:
        return wc[:-1]

def read_wildcards(allfiles=True):
    """
    
        Build a list of wildcards associated with available file filters with read ability.
        
        Parameters:
            allfiles    -    if True, add generic "All files (*.*)" entry to list
        
        Output:
            wildcard list (list)
    
    """
    wc = ""
    for x in modules:
        if x().can_read:
            wc = wc + x().wildcard() + "|"
    
    if allfiles:
        return wc + "All files (*.*)|*.*"
    else:
        return wc[:-1]

def save_wildcards(allfiles=True):
    """
    
        Build a list of wildcards associated with available file filters with save ability.
        
        Parameters:
            allfiles    -    if True, add generic "All files (*.*)" entry to list
        
        Output:
            wildcard list (list)
    
    """
    wc = ""
    for x in modules:
        if x().can_save:
            wc = wc + x().wildcard() + "|"
    
    if allfiles:
        return wc + "All files (*.*)|*.*"
    else:
        return wc[:-1]
