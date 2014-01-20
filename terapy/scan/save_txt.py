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

    Save to text file scan event class

"""

from terapy.scan.save import SaveBase
from terapy.files.text import Text

class Save_TXT(SaveBase):
    """
    
        Save to text file scan event class
    
    """
    __extname__ = "Save text"
    def __init__(self, parent = None):
        SaveBase.__init__(self, parent)
        self.is_visible = True
        self.filter = Text()
        
    def run(self, data):
        fname = self.make_filename()
        
        # split filename to compose name of info file
        fname = fname.split(".")
        ext = fname[-1]
        fname.append("")
        
        for n in range(self.m_id+1): # save what has been measured before calling 'save'
            fname[-2] = str(n+1)
            fname[-1] = ext
            data.data[n].filename = ".".join(fname)
            self.filter.save(".".join(fname), data.data[n])

    def check_validity(self, data):
        v = len(data.shape)
        if v<1 or v>2:
            return False
        else:
            return True
        