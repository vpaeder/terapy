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

	Excel file filter

"""

from terapy.files.base import FileFilter
import numpy as np
from terapy.core.dataman import DataArray
from time import strftime, localtime
from xlrd import open_workbook
from xlwt import Workbook
from xlutils.copy import copy
import os

class XLS(FileFilter):
	"""
	
		Excel file filter
	
	"""
	def __init__(self):
		FileFilter.__init__(self)
		self.ext = ["*.xls"]
		self.desc = "Excel workbooks"
		self.can_read = True
	
	def read(self,fname):
		# data name
		tname = self.strip(fname)
		# test file type
		rbook = open_workbook(fname)
		
		data = []
		for s in rbook.sheets():
			x = self.read_sheet(s)
			if x!=None:
				x.name = tname+" "+s.name
				data.append(x)
		return data
	
	def read_sheet(self,s):
		x = None
		if s.ncols==2: # 1D
			x = DataArray(shape=[s.nrows])
			for n in range(s.nrows):
				x.data[n] = s.cell(n,1).value
				x.coords[0][n] = s.cell(n,0).value
		elif s.ncols==3: # 3D
			if not(isinstance(s.cell(0,0).value,(int,long,float,complex))): # accept only numeric data
				return None
			c1 = np.zeros(s.nrows)
			c2 = np.zeros(s.nrows)
			d = np.zeros(s.nrows)
			for n in range(s.nrows):
				c1[n] = s.cell(n,0).value
				c2[n] = s.cell(n,1).value
				d[n] = s.cell(n,2).value
			c1 = np.unique(c1)
			c2 = np.unique(c2)
			d = d.reshape((len(c1),len(c2)))
			x = DataArray(shape=[len(c1),len(c2)])
			x.data = d
		return x
	
	def save(self, fname, arr, name="M_0"):
		if os.path.exists(fname):
			rbook = open_workbook(fname)
			book = copy(rbook)
			if rbook.sheet_names().count(name)==0:
				sheet = book.add_sheet(name)
				isheet = book.add_sheet(name+"_infos")
			else:
				sheet = book.get_sheet(rbook.sheet_names().index(name))
				isheet = book.get_sheet(rbook.sheet_names().index(name+"_infos"))
		else:
			book = Workbook()
			sheet = book.add_sheet(name)
			isheet = book.add_sheet(name+"_infos")
		
		if len(arr.shape) == 1: # 1D data
			self.save1D(sheet, arr)
		elif len(arr.shape) == 2: # 2D data
			self.save2D(sheet, arr)
		
		isheet.write(0,0,"Time")
		isheet.write(0,1,strftime("%d.%m.%Y, %H:%M:%S", localtime()))
		isheet.write(1,0,"Input device")
		isheet.write(1,1,"%s" % (arr.input))
		if len(arr.shape)==1:
			isheet.write(2,0,"Axis device")
			try:
				isheet.write(2,1,"%s" % (arr.axes[0]))
			except:
				pass
			n=4
		elif len(arr.shape)==2:
			isheet.write(2,0,"Axis X device")
			isheet.write(3,0,"Axis Y device")
			try:
				isheet.write(2,1,"%s" % (arr.axes[0]))
				isheet.write(3,1,"%s" % (arr.axes[1]))
			except:
				pass
			n=5

		isheet.write(n,0,"Scan parameters")
		if len(arr.shape)==1:
			isheet.write(n+1,0,"Range")
			isheet.write(n+1,1,min(arr.coords[0]))
			isheet.write(n+1,2,max(arr.coords[0]))
			isheet.write(n+2,0,"Steps")
			isheet.write(n+2,1,arr.shape[0])
		elif len(arr.shape)==2:
			isheet.write(n+1,0,"X - Range")
			isheet.write(n+1,1,min(arr.coords[0]))
			isheet.write(n+1,2,max(arr.coords[0]))
			isheet.write(n+2,0,"X - Steps")
			isheet.write(n+2,1,arr.shape[0])
			isheet.write(n+3,0,"Y - Range")
			isheet.write(n+3,1,min(arr.coords[1]))
			isheet.write(n+3,2,max(arr.coords[1]))
			isheet.write(n+4,0,"Y - Steps")
			isheet.write(n+4,1,arr.shape[1])
				
		book.save(fname)
		return True
	
	def save1D(self, sheet, arr):
		for i in range(arr.shape[0]):
			sheet.write(i,0,arr.coords[0][i])
			sheet.write(i,1,arr.data[i])

	def save2D(self, sheet, arr):
		for i in range(arr.shape[0]):
			for j in range(arr.shape[1]):
				sheet.write(i*arr.shape[1]+j,0,arr.coords[0][i])
				sheet.write(i*arr.shape[1]+j,1,arr.coords[1][j])
				sheet.write(i*arr.shape[1]+j,2,arr.data[i,j])
