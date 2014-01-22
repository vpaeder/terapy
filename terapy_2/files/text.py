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

	Text file filter

"""

from terapy.files.base import FileFilter
import numpy as np
from terapy.core.dataman import DataArray
from time import strftime, localtime

class Text(FileFilter):
	"""
	
		Text file filter
	
	"""
	def __init__(self):
		FileFilter.__init__(self)
		self.ext = ["*.dat","*.csv","*.txt"]
		self.desc = "ASCII data files"
	
	def read(self,fname):
		# data name
		tname = self.strip(fname)
		# test file type
		fp = open(fname, 'r')
		args = fp.readline().split('\t')
		fp.close()
		if len(args)==2: # 1D
			return self.read1D(fname,tname)
		elif len(args)==3: # 2D or 1D + std
			# must find out from support .txt file whether 1D or 2D
			sfname = fname.split('.')
			sfname[-1] = 'txt'
			sfname = ".".join(sfname)
			f = open(sfname,'r')
			fc = f.read()
			f.close()
			
			if fc.count("Axis X")==0:
				return self.read1Dv(fname,tname)
			else:
				return self.read2D(fname,tname)
		elif len(args)==4: # 2D + std
			return self.read2D(fname,tname)
		
		return None

	def read1D(self, fname, tname):
		# open file and read column 0 and 1, separator is tab
		data_t = []
		data_x = []
		fp = open(fname, 'r')
		for l in fp:
			args = l.split('\t')
			if args[0][0].isalpha() == 0:
				data_t.append(float(args[0]))
				data_x.append(float(args[1]))
		fp.close()
		
		data = DataArray(name=tname, shape=[len(data_t)])
		data.coords = [np.array(data_t)]
		data.data = np.array(data_x)
		data.shape = [len(data_x)]
		return [data]

	def read1Dv(self, fname, tname):
		# open file and read column 0, 1 and 2 (variance), separator is tab
		data_t = []
		data_x = []
		data_v = []
		fp = open(fname, 'r')
		for l in fp:
			args = l.split('\t')
			if args[0][0].isalpha() == 0:
				data_t.append(float(args[0]))
				data_x.append(float(args[1]))
				data_v.append(float(args[2]))
		fp.close()
		if len(data_v)<len(data_x):
			data_v = np.zeros(len(data_x))
		
		data1 = DataArray(name=tname+" 0", shape=[len(data_t)])
		data2 = DataArray(name=tname+" 1", shape=[len(data_t)])
		
		data1.coords = [np.array(data_t)]
		data1.data = np.array(data_x)
		data1.shape = [len(data_x)]
		data2.coords = [np.array(data_t)]
		data2.data = np.array(data_v)
		data2.shape = [len(data_v)]
		return [data1, data2]

	def read2D(self, fname, tname):
		fp = open(fname, 'r')
		x = []
		y = []
		z = []
		for l in fp:
			args = l.split('\t')
			if args[0][0].isalpha() == 0:
				x.append(float(args[0]))
				y.append(float(args[1]))
				z.append(float(args[2]))
		fp.close()
		x = np.array(x)
		y = np.array(y)
		z = np.array(z)
		
		data_x = np.unique(x)
		data_y = np.unique(y)
		data_2d = np.zeros((len(data_x),len(data_y)))
		if False: # accurate but very slow way of sorting 
			for nx in range(len(data_x)):
				for ny in range(len(data_y)):
					data_2d[nx,ny] = z[(x==data_x[nx])*(y==data_y[ny])]
		else:
			for ny in range(len(data_y)):
					data_2d[:,ny] = z[ny*len(data_x):(ny+1)*len(data_x)]
		
		data = DataArray(name=tname, shape=list(data_2d.shape))
		data.coords.append(data_x)
		data.coords.append(data_y)
		data.data = data_2d
		return [data]
	
	def save(self, fname, arr):
		if len(arr.shape)<1 or len(arr.shape)>2:
			return False
		fname = fname.split(".")
		f = open(".".join(fname), 'w')
		
		if len(arr.shape)==1: # 1D file
			for r in range(arr.shape[0]):
				f.write("%e\t%e\n" % (arr.coords[0][r], arr.data[r]))
		elif len(arr.shape)==2: # 2D file
			for r in range(arr.shape[0]):
				for s in range(arr.shape[1]):
					f.write("%e\t%e\t%e\n" % (arr.coords[0][r], arr.coords[0][s], arr.data[r,s]))
		f.close()
		
		fname[-1] = "txt"
		f = open(".".join(fname), 'w')
		f.write("Information for scan from %s\n\n" % (strftime("%d.%m.%Y, %H:%M:%S", localtime())))
		f.write("Input device:\n\t%s\n" % (arr.input))
		if len(arr.shape)==1:
			try:
				f.write("Axis device:\n\t%s\n" % (arr.axes[0]))
			except:
				f.write("Axis device:\n\t%s\n" % (""))
		elif len(arr.shape)==2:
			try:
				f.write("Axis X device:\n\t%s\n" % (arr.axes[0]))
				f.write("Axis Y device:\n\t%s\n" % (arr.axes[1]))
			except:
				f.write("Axis X device:\n\t%s\n" % (""))
				f.write("Axis Y device:\n\t%s\n" % (""))
		
		f.write("\nScan parameters:\n")
		if len(arr.shape)==1:
			f.write("Range: " + str(min(arr.coords[0])) + " - " + str(max(arr.coords[0])))
			f.write("Steps: %f\n" % (arr.shape[0]))
		elif len(arr.shape)==2:
			f.write("X - Range: " + str(min(arr.coords[0])) + " - " + str(max(arr.coords[0])))
			f.write("X - Steps: %f\n" % (arr.shape[0]))
			f.write("Y - Range: " + str(min(arr.coords[1])) + " - " + str(max(arr.coords[1])))
			f.write("Y - Steps: %f\n" % (arr.shape[1]))
		f.close()
		return True
	
