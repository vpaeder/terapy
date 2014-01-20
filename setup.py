#!/usr/bin/env python
from distutils.core import setup
from setuptools.command import install_scripts
try:    
	# import py2exe for windows exe creation
	import py2exe
except:
	pass

setup(name='terapy',
      version='2.00b5',
      description='Graphical interface for scientific measurements',
      author='Vincent Paeder, Daniel Dietze',
      author_email='vincent.paeder@tuwien.ac.at',
      url='',
      py_modules=['tera'],
      packages=['terapy','terapy.core','terapy.files','terapy.filters','terapy.hardware','terapy.hardware.axes','terapy.hardware.input','terapy.icons','terapy.plot','terapy.scan'],
      package_data={'terapy':['icons/*.png','icons/*.ico']},
      entry_points={'console_scripts':['terapy = tera:main']},
	  console=['tera.py'],
	  install_requires=['wxPython','matplotlib','numpy','scipy','quantities','h5py', 'xlrd', 'xlwt', 'xlutils' ,'statsmodels', 'pyWavelets', 'pandas' ,'PyVISA'],
)
