#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# $Id$


import os, sys, re
import math, cmath
import zipfile
from touchstone import Touchstone
from beadparts import parts


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
	def MHz(self): return [ f * 1e-6 for f in self._f ]
	@property
	def R(self): return [ z.real for z in self._z ]
	@property
	def X(self): return [ z.imag for z in self._z ]
	@property
	def Z(self): return [ abs(z) for z in self._z ]

	def _findex(self, frequency):
		for i, f in enumerate(self._f):
			if f >= frequency:
				return i

	def L(self, f=1e6):
		"""Inductance at given frequency. Uses linear interpolation.

		@param f   Frequency as float
		@ret inductance as float or None
		"""
		z = self.z(f)
		return z.imag / (2.0*cmath.pi*f) if z is not None else None

	def z(self, f=100e6):
		"""Complex impedance at given frequency. uses linear interpolation

		@param f   Frequency as float
		@ret complex impedance or None
		"""
		i = self._findex(f)
		if i is None: return
		if i == 0: return self._z[0]
		delta_f = (f - self._f[i]) / (self._f[i-1] - self._f[i])
		return self._z[i-1] + delta_f * (self._z[i-1] - self._z[i])

	def xpoint(self):
		"""X-R cross point (interpolated)

		@ret frequency as float or None
		"""
		x_was_above_r = False

		for i, (f, z) in enumerate(zip(self._f, self._z)):

			if z.imag > z.real:
				# it's possible that at low frequency X is smaler than R, so ...
				x_was_above_r = True

			if x_was_above_r and z.real >= z.imag:
				# calc the cross point
				dz = self._z[i] - self._z[i-1]
				dxy = self._f[i] * self._z[i-1] - self._z[i] * self._f[i-1]
				try:
					fx = (dxy.real - dxy.imag) / (dz.imag - dz.real)
					assert (fx <= f)
				except ZeroDivisionError:
					return None

				return fx


def code2imp(code):
	"""Most parts have it value encoded with three decimals numbers
	where the first two numbers are the matissa and the third the exponent.
	"""
	return float(code[:2]) * 10.0**float(code[2])


def in_range(value, range):
	return range[0] <= value <= range[1]


def filescan(size, impedance, inductance=None):
	""" Scan all files defined by @parts and find size, impedance
	    and optional inductance matching parts.

	@param size        Part size as string. Possible values are as defined by @scmap.
	@param impedance   Tuple (Zmin, Zmax)
	@param inductance  Tuple (Lmin, Lmax) or None
	"""

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


def eng_fmt(value, fmt='.3'):
	""" Float formating which engineers like, 10**(3*n)
	"""
	if value is None: return str(None)

	n = 0
	while not (1.0 <= abs(value) < 1000.0):
		if abs(value) >= 1000.0:
			value *= 1e-3
			n += 3
		else:
			value *= 1e3
			n -= 3

	expo = {15:'P', 12:'T', 9:'G', 6:'M', 3:'k', 0:'',-3:'m', -6:'u', -9:'n', -12:'p', -15:'f'}
	return ('{:%sf}{}' % fmt).format(value, expo[n])


def plot(bead_data, frange=(1e6, 1e9), rmin=1.0, scale='loglog'):
	""" Plots the bead_data

	@param bead_data   List,Tuple of BeadData objects
	@param frange      List,Tuple (f-min, f-max), diagram's frequency limits
	@param rmin        diagram's minimum resistance
	@param scale       diagram scaling, possible values are [ loglog | linlog | loglin | linlin ]
	"""

	fig = plt.figure()
	cols = int(math.sqrt ( len(bead_data) ))
	for i, bdata in enumerate(bead_data):
		ax = plt.subplot((len(bead_data) + cols-1) / cols, cols, 1+i)
		ax.grid()

		ax.set_xscale(scale[:3])
		ax.set_yscale(scale[3:])
		ax.plot(bdata.MHz, bdata.R, 'b')
		ax.plot(bdata.MHz, bdata.X, 'g')
		ax.plot(bdata.MHz, bdata.Z, 'r')


		ax.set_xlabel('MHz')
		ax.set_ylim(ymin=rmin)
		ax.set_xlim(xmin=frange[0]*1e-6, xmax=frange[1]*1e-6 )


		#~ ax.set_title(bdata.name)
		ax.text(0.05, 0.95, bdata.name,
			verticalalignment='top', horizontalalignment='left',
			transform=ax.transAxes,
			fontsize=10)

	plt.show()


def info(bead_data):
	""" Prints some bead data to stdout.
	- inductance @ 1MHz
	- cross point frequency (X=R)
	- impedance @ 1, 10 and 100MHz

	@param bead_data   List,Tuple of BeadData objects
	"""

	for bdata in bead_data:
		print ('{:<20}: L = {}H, X=R @ {}Hz, Z = {:>.2f} @1MHz, {:>.2f} @10MHz, {:>.2f} @100MHz'.format(bdata.name,
				eng_fmt(bdata.L(1e6)),
				eng_fmt(bdata.xpoint(), '.2'),
				abs(bdata.z(1e6)),
				abs(bdata.z(10e6)),
				abs(bdata.z(100e6)) )
			)
