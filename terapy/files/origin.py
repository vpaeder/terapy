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

    Origin OPJ file filter

"""

from terapy.files.base import FileFilter
from terapy.core.dataman import DataArray 
from struct import unpack, pack
import numpy as np
from time import strftime, localtime

class OPJ(FileFilter):
    """
    
        Origin OPJ file filter
        
        Parsing routine adapted from SciDAVis project (http://sourceforge.net/projects/scidavis/)
    
    """
    def __init__(self):
        FileFilter.__init__(self)
        self.ext = ["*.opj"]
        self.desc = "Origin project files"
        self.can_read = True
        self.can_save = False
        self.multi_data = True
        self.valueflags = {1:'B',2:'h',4:'i',8:'d'}
    
    def read(self,fname):
        # adapted from scidavi origin file parser
        f = open(fname,'r')
        # get version
        v = self.get_version(f)
        if not(v):
            return None # not an origin file or unknown format anyway
        
        # header
        header = self.read_block(f)
        if self.read_blocksize(f)!=0: # malformed header
            return None
        if len(header)>27: # version 6.1 or newer
            v = unpack("<d",header[27:35])[0]
            version = int(v*10)/10.
            release = int((v-version)*10000+0.5)
        
        # read data sets
        sheets = [] 
        header = self.read_block(f)
        while not(header==None):
            data = self.read_block(f)
            mask = self.read_block(f)
            
            (datatype,) = unpack("<h",header[22:24])
            (nr,) = unpack("<I",header[25:29])
            (valuesize,) = unpack("<B",header[61])
            #(datatype_u,) = unpack("<B",header[63])
            name = header[88:88+25].partition('\0')[0].strip().split("_")
            colname = name.pop()
            name = "_".join(name)
            
            if sheets.count(name)==0: # new sheet
                sheets.append(Spreadsheet(name))
                cursheet = sheets[-1]
            else:
                cursheet = sheets[sheets.index(name)]
            cursheet.AppendColumn(colname)
            
            nr = len(data)/valuesize
            if valuesize<10:
                fmt = '<%d' % nr + self.valueflags[valuesize]
                cursheet.SetValues(unpack(fmt,data))
            else:
                if (datatype & 256 == 256): # numeric+text
                    fmt = '<cc%ds' % (valuesize-2)
                    splitlist = map(lambda x:unpack(fmt,x),map(lambda x:"".join(x),[map(lambda x:x,data)[i:i+valuesize] for i in range(0, len(data), valuesize)]))
                    cursheet.SetValues(map(lambda x: unpack('d',x[2][:8])[0] if x[0]=='\0' else x[2][0:x[2].index('\0')], splitlist))
                else:
                    fmt = '%ds' % valuesize
                    splitlist = map(lambda x:unpack(fmt,x)[0],map(lambda x:"".join(x),[map(lambda x:x,data)[i:i+valuesize] for i in range(0, len(data), valuesize)]))
                    cursheet.SetValues(map(lambda x:x[0:x.index('\0')], splitlist))
            
            header = self.read_block(f) # next block
        
        f.close()
        return map(lambda x: x.GetDataArray(), sheets)
        
        # next stuff not necessary for simple reading - need to be studied for writing
        # read windows list
        header = self.read_block(f)
        while header != None:
            window_name = header[2:27].partition('\0')[0].strip()
            (w_left, w_top, w_right, w_bottom, w_width, w_height) = unpack("<6H",header[27:39])
            (w_type,) = unpack("<B",header[50])
            w_kind = header[69:79].partition('\0')[0].strip()
            try:
                (w_title_type, w_state) = unpack('<BB',header[105:107])
            except:
                pass
            
            if w_type<24:
                w_type = 'Graph'
            elif w_type<80:
                w_type = 'Layout'
            elif w_type<84:
                w_type = 'Worksheet'
            else:
                w_type = 'Matrix'
            
            try:
                (w_cdate, w_mdate) = map(lambda x: strftime('%F %T',localtime(int((x-2440587.5)*86400))),unpack("<2d", header[115:131]))
            except:
                pass
            
            # read layer list
            header_l = self.read_block(f)
            while header_l != None:
                # read sublayer list
                header_sl = self.read_block(f)
                while header_sl != None:
                    data_sl1 = self.read_block(f)
                    data_sl2 = self.read_block(f)
                    data_sl3 = self.read_block(f)
                    header_sl = self.read_block(f)
                
                # read curve list
                header_c = self.read_block(f)
                while header_c != None:
                    data_c = self.read_block(f)
                    header_c = self.read_block(f)
                
                # read axis break list
                header_ab = self.read_block(f)
                while header_ab != None:
                    data_ab = self.read_block(f)
                    header_ab = self.read_block(f)
                
                # read axis parameter list
                for x in [1,2,3]:
                    header_ap = self.read_block(f)
                    while header_ap != None:
                        data_ap = self.read_block(f)
                        header_ap = self.read_block(f)
                
                header_l = self.read_block(f) # layers
            header = self.read_block(f) # windows
                
            # read parameter list
            param_name = f.readline().strip()
            while param_name != '\0':
                param_value = unpack('<d',f.read(8))
                param_name = f.readline().strip()
            self.read_blocksize(f) # should be 0
                
            # read note list
            header_n = self.read_block(f)
            while header_n != None:
                data_nl = self.read_block(f)
                data_nc = self.read_block(f)
                header_n = self.read_block(f)
            
            # read project tree
            preamble1 = self.read_block(f)
            preamble2 = self.read_block(f)
            self.readFolderTree(f)
            
            # read attachment list
            header_a = self.read_block(f)
            # here - should process attachments - not sure I care
        f.close()
        
        return map(lambda x: x.GetDataArray(), sheets)
    
    def readFolderTree(self, f):
        header = self.read_block(f)
        self.read_blocksize(f) # 0 block
        name = self.read_block(f)
        self.read_blocksize(f) # 0 block
        (numfiles,) = unpack('<i',self.read_block(f))
        for i in range(numfiles):
            self.read_blocksize(f) # 0 block
            header_f = self.read_block(f)
            self.read_blocksize(f) # 0 block
        (numfolders,) = unpack('<i',self.read_block(f))
        for i in range(numfolders):
            self.readFolderTree(f)
    
    def save(self, fname, arr, name="M_0"):
        import os
        f = open(os.path.dirname(__file__)+'/default.opj','r')
        fsize = os.fstat(f.fileno()).st_size
        fw = open(fname,'w')
        self.get_version(f) # pass version
        self.read_block(f) # pass header
        self.read_blocksize(f) # pass 0 char
        w = f.tell()
        f.seek(0)
        fw.write(f.read(w))
                
        # build data sets
        header = self.read_block(f)
        orig = header[88:88+25]
        data = self.read_block(f)
        mask = self.read_block(f)
        
        values = [x for x in arr.coords]
        if len(arr.shape)==1: # 1D
            values.append(arr.data)
        elif len(arr.shape)==2: # 2D
            values.append(arr.data.reshape(arr.shape[0]*arr.shape[1]))
        
        for i in range(len(values)):
            header = header.replace(orig, (name[:24] + "_" + chr(65+i)).ljust(25,'\0'))
            self.write_block(fw,header)
            data = "".join(map(lambda x: '\0\0' + pack('<d',x), values[i]))
            self.write_block(fw,data)
            self.write_block(fw,mask)

        
        [self.read_block(f) for x in [1,2,3]] # read 3 blocks
        f.close()
        fw.close()
    
    def write_block(self,f,block):
        if block!=None:
            bsize = pack('<I',len(block)) + '\n'
            f.write(bsize+block+'\n')
        else:
            bsize = pack('<I',0) + '\n'
            f.write(bsize)
    
    def read_blocksize(self,f):
        b = f.read(5)
        if b[-1]!='\n':
            return 0
        else:
            return unpack('<I',b[:-1])[0]
    
    def read_block(self,f,sz=0):
        if sz<=0: sz = self.read_blocksize(f)
        if sz<=0: return None
        block = f.read(sz)
        if f.read(1) != '\n': return None # malformed block
        return block 
    
    def get_version(self,f):
        v = f.readline().strip()
        if v.find('#')==-1:
            return False
        else:
            v = v.split()
            if v[0]!='CPYA':
                return False
            else:
                return v[1]

class Spreadsheet():
    def __init__(self, name=""):
        self.name = name
        self.columns = []
        self.col = 0
        self.row = 0
        
    def __eq__(self,sheet):
        if isinstance(sheet,Spreadsheet):
            return sheet.name == self.name
        elif isinstance(sheet,(str,unicode)):
            return sheet == self.name
    
    def AppendColumn(self,name=""):
        self.columns.append(Column(name))
        self.col = len(self.columns)-1
        self.row = 0
    
    def AddValue(self,value):
        self.columns[self.col].AddValue(value)
        self.row = self.columns[self.col].row
    
    def SetValues(self,values):
        self.columns[self.col].SetValues(values)
        self.row = self.columns[self.col].row
        
    def GetColumnByName(self,name):
        cp = map(lambda x:x.name==name,self.columns)
        if cp.count(True)>0:
            return self.columns[cp.index(True)]
        else:
            return None
    
    def GetDataArray(self):
        data = np.array(map(lambda x:np.array(x.data),self.columns))
        arr = None
        if data.shape[0]==2: # 1D
            arr = DataArray(shape=[data.shape[1]],name=self.name)
            arr.name = self.name
            arr.coords[0] = data[0,:]
            arr.data = data[1,:]
        elif data.shape[0]==3: # 2D
            cx = np.unique(data[0,:])
            cy = np.unique(data[1,:])
            arr = DataArray(shape=[len(cx),len(cy)],name=self.name)
            arr.coords[0] = cx
            arr.coords[1] = cy
            arr.data = data[2,:].reshape((len(cx),len(cy)))
        return arr

class Column():
    def __init__(self,name=""):
        self.row = 0
        self.data = []
        self.name = name
    
    def AddValue(self, value):
        self.data.append(value)
        self.row = len(self.data)-1
    
    def SetValues(self, values):
        self.data = values
        self.row = len(self.data)-1

#x=OPJ()
#p=x.read('../60.opj')
#x.save('../zorg.opj',p[0],'MEUUUH')
