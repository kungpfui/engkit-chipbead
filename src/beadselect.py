#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# $Id$

from collections import namedtuple
import os, sys, re
import math, cmath
import zipfile


NameConv = namedtuple('NameConv', ['regex_fn','scmap'])

manufacturer = dict(
	murata     = NameConv(r'.*(?P<size_code>\d{2})[A-Z]{2}(?P<imp_code>\d{3}).*',
	             {'0201' : '03', '0402' : '15', '0603' : '18', '0805' : '21', '1206' : '31'} ),

	tayo_yuden = NameConv(r'.*(?P<size_code>\d{4})_.*(?P<imp_code>\d{3}).*',
	             {'0402' : '1005', '0603' : '1608', '0805' : '2012'} ),

	tdk        = NameConv(r'.*(?P<size_code>\d{4})[A-Z](?P<imp_code>\d{3}).*',
	             {'0402' : '1005', '0603' : '1608', '0805' : '2012'} ),

	wuerth     = NameConv(r'^(?P<size_code>\d{7}).*',
	             {'0402' : '7427927', '0603' : '7427926', '0805' : '7427920'} ),
)

parts = {
	# murata parts, http://www.murata.com/en-us/tool/sparameter/ferritebead
	'blm15_s_v10.zip': manufacturer['murata'],
	'blm18_s_v10.zip': manufacturer['murata'],
	'blm21_s_v10.zip': manufacturer['murata'],

	# TDK parts, https://product.tdk.com/info/en/technicalsupport/tvcl/general/beads.html
	'beads_commercial_signal_mmz1005_spara.zip': manufacturer['tdk'],
	'beads_commercial_signal_mmz1005-e_spara.zip': manufacturer['tdk'],
	'beads_commercial_signal_mmz1005-v_spara.zip': manufacturer['tdk'],
	'beads_commercial_power_mpz1005_spara.zip': manufacturer['tdk'],
	'beads_commercial_signal_mmz1608_spara.zip': manufacturer['tdk'],
	'beads_commercial_power_mpz1608_spara.zip': manufacturer['tdk'],

	# Tayo Yuden parts, http://www.yuden.co.jp/ut/product/support/pdf_spice_spara/
	'BK.zip': manufacturer['tayo_yuden'],
	'BKP.zip': manufacturer['tayo_yuden'],
	'FBM.zip': manufacturer['tayo_yuden'],

	# Würth parts, http://www.we-online.de/web/de/electronic_components/toolbox_pbs/S_Parameter_1.php
	'WE_CBF_0402.zip': manufacturer['wuerth'],
	'WE_CBF_0603.zip': manufacturer['wuerth'],
	'WE_CBF_0805.zip': manufacturer['wuerth'],
}


from touchstone import Touchstone
class BeadData(object):
	def __init__(self, fileobj):
		self.name = os.path.basename(fileobj.name)[:-4]
		self._f = []
		self._z = []

		for d in Touchstone(fileobj):
			# sometimes the DC value is there, throw it away
			if d.f > 0.0:
				self._f.append(d.f)
				self._z.append(d.Z)

	@property
	def MHz(self): return [ f * 1e-6 for f in self._f]
	@property
	def R(self): return [ z.real for z in self._z]
	@property
	def X(self): return [ z.imag for z in self._z]
	@property
	def Z(self): return [ abs(z) for z in self._z]

	def _findex(self, frequency):
		for i, f in enumerate(self._f):
			if f >= frequency:
				return i

	def L(self, f=1e6):
		z = self.z(f)
		return z.imag / (2.0*cmath.pi*f) if z is not None else None

	def z(self, f=100e6):
		i = self._findex(f)
		if i is None: return
		if i == 0: return self._z[0]
		delta_f = (f - self._f[i]) / (self._f[i-1] - self._f[i])
		return self._z[i-1] + delta_f * (self._z[i-1] - self._z[i])


def code2imp(code):
	return float(code[:2]) * 10.0**float(code[2])

def in_range(value, range):
	return range[0] <= value <= range[1]

def filescan(size, impedance, inductance=None):
	bead_data_lst = []

	for filename in parts:
		size_code = parts[filename].scmap.get(size)
		# this can't match in any way so just go further with the next file
		if size_code is None: continue

		if not os.path.exists(filename):
			print("Warning: file does not exist '{}'.\nUncomment in 'parts' dictionary to get rid of this message.".format(filename))
			continue

		with zipfile.ZipFile(filename, 'r') as zf:
			for name in zf.namelist():
				#~ print name
				mobj = re.match(parts[filename].regex_fn, name)
				if mobj:
					d = mobj.groupdict()
					if d.get('size_code') == size_code \
							and (d.get('imp_code') is None \
							or in_range( code2imp(d.get('imp_code')), impedance) ):

						with zf.open(name, 'r') as subzf:
							bd = BeadData( subzf )

						# no impedance code in filename? check now by s-parameters
						if d.get('imp_code') is None and not in_range( abs(bd.z()), impedance):
							continue

						if inductance:
							if in_range( bd.L(), inductance):
								bead_data_lst.append( bd )
						else:
							bead_data_lst.append( bd )

	if sys.version_info[0] >= 3:
		bead_data_lst.sort(key=lambda x: x.L())
	else:
		bead_data_lst.sort(cmp=lambda x,y: cmp(x.L(), y.L()))

	return bead_data_lst



import matplotlib.pyplot as plt

def eng_fmt(value):
	n = 0
	while value < 1.0:
		value *= 1000.0
		n += 1
	expo = {0:'', 1:'m', 2:'u', 3:'n', 4:'p'}
	return '{:.3f}{}'.format(value, expo[n])


def plot(bead_data, frange=(1e6, 1e9), rmin=1.0):
	fig = plt.figure()
	cols = int(math.sqrt ( len(bead_data) ))
	for i, bdata in enumerate(bead_data):
		ax = plt.subplot((len(bead_data) + cols-1) / cols, cols, 1+i)
		ax.grid()

		ax.loglog(bdata.MHz, bdata.R, 'b')
		ax.loglog(bdata.MHz, bdata.X, 'g')
		ax.loglog(bdata.MHz, bdata.Z, 'r')

		ax.set_xlabel('MHz')
		ax.set_ylim(ymin=rmin)
		ax.set_xlim(xmin=frange[0]*1e-6, xmax=frange[1]*1e-6 )

		#~ ax.set_title(bdata.name)
		ax.text(0.95, 0.01, bdata.name,
			verticalalignment='bottom', horizontalalignment='right',
			transform=ax.transAxes,
			fontsize=8)
	plt.show()


def info(bead_data):
	for bdata in bead_data:
		print ('{:<16}: L = {}H, Z = {:>.3f} @1MHz, {:>.3f} @10MHz, {:>.3f} @100MHz'.format(bdata.name,
				eng_fmt(bdata.L()),
				abs(bdata.z(1e6)),
				abs(bdata.z(10e6)),
				abs(bdata.z(100e6)) )
			)
