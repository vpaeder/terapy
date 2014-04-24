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

	HDF5 file filter

"""

from terapy.files.base import FileFilter
from terapy.core.dataman import DataArray
import h5py as h5
from time import strftime, localtime
from numpy import number as npnumber
from xml.dom import minidom

class HDF5(FileFilter):
	"""
	
		HDF5 file filter
	
	"""
	def __init__(self):
		FileFilter.__init__(self)
		self.ext = ["*.h5","*.dat"]
		self.desc = "HDF5 files"
		self.multi_data = True

	def read(self,fname):
		try:
			f = h5.File(fname,'r')
		except:
			return None
		
		# data name
		tname = self.strip(fname)

		data = []
		xml = ""
		for x in f.items():
			if x[1].dtype==npnumber:
				data.append(DataArray(shape=list(x[1].shape),name=tname+" "+x[0]))
				data[-1].data = x[1][...]
				for n in range(len(data[-1].shape)):
					data[-1].coords[n] = x[1].attrs['Coordinates '+str(n)]
			else:
				# try to see if it is an xml tree
				try:
					minidom.parseString(str(x[1][...]))
					xml = str(x[1][...])
				except:
					pass # not XML
		if xml!="":
			for x in data:
				# add event tree to data arrays
				x.xml = xml
		
		f.close()
		return data
	
	def save(self, fname, arr, name="M_0"):
		f = h5.File(fname,'a')
		# write data set
		dset = f.create_dataset(name, tuple(arr.shape), dtype='float64')
		dset[...] = arr.data
		# add axes/input and additional infos
		dset.attrs['Number of axes'] = len(arr.axes)
		for m in range(len(arr.axes)):
			try:
				dset.attrs['Axis '+str(m)] = "%s" % arr.axes[m]
			except:
				dset.attrs['Axis '+str(m)] = ""
			dset.attrs['Coordinates '+str(m)] = arr.coords[m]
		dset.attrs['Input'] = "%s" % (arr.input)
		dset.attrs['Time'] = strftime("%d-%m-%Y %H:%M:%S", localtime())
		f.close()
