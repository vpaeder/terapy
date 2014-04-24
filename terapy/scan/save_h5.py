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

    Save to HDF5 scan event class

"""

from terapy.scan.save import SaveBase
import h5py as h5
from terapy.files.hdf5 import HDF5

class Save_H5(SaveBase):
    """
    
        Save to HDF5 scan event class
    
    """
    __extname__ = "Save HDF5"
    def __init__(self, parent = None):
        SaveBase.__init__(self, parent)
        self.is_visible = True
        self.filter = HDF5()
        
    def run(self, data):
        fname = self.make_filename()
        
        f = h5.File(fname,'w')
        f.create_dataset("Event tree",data=data.xml) # store event tree
        f.create_dataset("System state",data=data.systemState) # store system state
        f.close()
        for n in range(self.m_id+1): # save what has been measured before calling 'save'
            data.data[n].filename = fname
            self.filter.save(fname, data.data[n],name="M_"+str(n))
