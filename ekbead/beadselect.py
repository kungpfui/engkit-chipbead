#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The bead selecting algorithm implementation.

1. call filescan()
2. call plot() and/or info() with the returned data of filescan() as argument.
"""

import os
import sys
import re
import math
import cmath
import zipfile
import matplotlib.pyplot as plt
from .touchstone import Touchstone
from .beadparts import PARTS


class BeadData(object):
    """Data collection of a chip bead."""

    def __init__(self, fileobj):
        """c'tor
        @param fileobj  file-like object
        """
        self.name = os.path.basename(fileobj.name)[:-4]
        self._f = []
        self._z = []

        for dataset in Touchstone(fileobj):
            # sometimes the DC value is there, throw it away
            if dataset.f > 0.0:
                self._f.append(dataset.f)
                self._z.append(dataset.Z)

    @property
    def MHz(self):
        "List of frequencies as float MHz."
        return [freq * 1e-6 for freq in self._f]

    @property
    def R(self):
        "List of resistance values as float."
        return [z.real for z in self._z]

    @property
    def X(self):
        "List of reactance values as float."
        return  [z.imag for z in self._z]

    @property
    def Z(self):
        "List of absolute impedance values as float."
        return [abs(z) for z in self._z]

    def _findex(self, freq_to_find):
        """Finds list index where frequency >= freq_to_find
        @param freq_to_find   Hz as float
        @ret list index as int
        """
        for i, freq in enumerate(self._f):
            if freq >= freq_to_find:
                return i

    def L(self, freq=1e6):
        """Inductance at given frequency. Uses linear interpolation.

        @param freq   Frequency (Hz) as float
        @ret inductance as float or None
        """
        z = self.z(freq)
        return z.imag / (2.0 * cmath.pi * freq) if z is not None else None

    def z(self, f=100e6):
        """Complex impedance at given frequency, uses linear interpolation

        @param f   Frequency as float
        @ret complex impedance or None
        """
        i = self._findex(f)
        if i is None:
            return
        if i == 0:
            return self._z[0]
        delta_f = (f - self._f[i]) / (self._f[i-1] - self._f[i])
        return self._z[i-1] + delta_f * (self._z[i-1] - self._z[i])

    def xpoint(self):
        """X-R cross point (interpolated)

        @ret frequency as float or None
        """
        x_was_above_r = False

        for i, z in enumerate(self._z):
            if z.imag > z.real:
                # it's possible that at low frequency X is smaller than R, so ...
                x_was_above_r = True

            if x_was_above_r and z.real >= z.imag:
                # calc the cross point
                delta_z = self._z[i] - self._z[i-1]
                delta_xy = self._f[i] * self._z[i-1] - self._z[i] * self._f[i-1]
                try:
                    freq_intrplt = (delta_xy.real - delta_xy.imag) / (delta_z.imag - delta_z.real)
                    assert freq_intrplt <= self._f[i]
                except ZeroDivisionError:
                    return None

                return freq_intrplt

    def max_Z(self):
        z_max = max(self.Z)
        return z_max, self._f[self.Z.index(z_max)]


def code2imp(code):
    """Most parts have it's value encoded with three decimals numbers
    where the first two numbers are the matissa and the third the exponent.
    """
    return float(code[:2]) * 10.0**float(code[2])


def in_range(value, range):
    """Is value in range (inclusive).
    @param value  float, int
    @param range  tuple(min_, max_)
    @ret bool
    """
    return range[0] <= value <= range[1]


def filescan(size, impedance, inductance=None):
    """ Scan all files defined by @PARTS and find size, impedance
        and optional inductance matching parts.

    @param size        Part size as string. Possible values are as defined by @scmap.
    @param impedance   Tuple (Zmin, Zmax)
    @param inductance  Tuple (Lmin, Lmax) or None
    """

    bead_data_lst = []

    for filename in PARTS:
        size_code = PARTS[filename].scmap.get(size)
        # this can't match in any way so just go further with the next file
        if size_code is None:
            continue

        if not os.path.exists(filename):
            print("Warning: file does not exist '{}'.\nUncomment in 'PARTS' dictionary to get rid of this message.".format(filename))
            continue

        with zipfile.ZipFile(filename, 'r') as zipobj:
            for name in zipobj.namelist():
                #~ print name
                mobj = re.match(PARTS[filename].regex_fn, name)
                if mobj:
                    mdict = mobj.groupdict()
                    if mdict.get('size_code') == size_code \
                       and (mdict.get('imp_code') is None \
                       or in_range(code2imp(mdict.get('imp_code')), impedance)):

                        with zipobj.open(name, 'r') as zip_fileobj:
                            bd = BeadData(zip_fileobj)

                        # no impedance code in filename? check now by s-parameters
                        if mdict.get('imp_code') is None and not in_range(abs(bd.z()), impedance):
                            continue

                        if inductance:
                            if in_range(bd.L(), inductance):
                                bead_data_lst.append(bd)
                        else:
                            bead_data_lst.append(bd)

    if sys.version_info[0] >= 3:
        bead_data_lst.sort(key=lambda x: x.L())
    else:
        # python 2.x
        bead_data_lst.sort(cmp=lambda x, y: cmp(x.L(), y.L()))

    return bead_data_lst



def eng_fmt(value, fmt='.3'):
    """ Float formating which engineers like, 10**(3*n)
    @param value  a float value
    @param fmt    format to use within @format function

    @ret string
    """
    if value is None:
        return str(None)

    prefix = 'yzafpnum kMGTPEZY'
    n = prefix.index(' ')
    while not (1.0 <= abs(value) < 1000.0) and 0 < n < len(prefix):
        scale = -1 if abs(value) < 1.0 else +1
        n += scale
        value *= 10.0 ** float(scale * -3)

    return ('{:%sf}{}' % fmt).format(value, prefix[n].strip())


def plot(bead_data, frange=(1e6, 1e9), rmin=1.0, scale='loglog'):
    """ Plots the bead_data

    @param bead_data   List,Tuple of BeadData objects
    @param frange      List,Tuple (f-min, f-max), diagram's frequency limits
    @param rmin        diagram's minimum resistance
    @param scale       diagram scaling, possible values are [ loglog | linlog | loglin | linlin ]
    """

    # matplotlib does not know 'lin'
    def scale_mpl(s): return dict(lin='linear').get(s, s)

    fig = plt.figure()
    fig.canvas.set_window_title('Electronics Engineering Kit - SMD Chip Bead Selector')
    cols = int(math.sqrt(len(bead_data)))
    for i, bdata in enumerate(bead_data):
        axis = plt.subplot((len(bead_data) + cols-1) // cols, cols, 1+i)
        axis.grid()

        axis.set_xscale(scale_mpl(scale[:3]))
        axis.set_yscale(scale_mpl(scale[3:]))
        axis.plot(bdata.MHz, bdata.R, 'b')
        axis.plot(bdata.MHz, bdata.X, 'g')
        axis.plot(bdata.MHz, bdata.Z, 'r')


        axis.set_xlabel('MHz')
        axis.set_ylim(ymin=rmin)
        axis.set_xlim(xmin=frange[0]*1e-6, xmax=frange[1]*1e-6)


        #~ axis.set_title(bdata.name)
        axis.text(0.05, 0.95,
                  bdata.name,
                  verticalalignment='top',
                  horizontalalignment='left',
                  transform=axis.transAxes,
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
        max_z, max_z_freq = bdata.max_Z()
        print('{:<20}: L = {:>8}H, X=R @ {:>7}Hz, Zmax = {:>6.1f} @ {:>6}Hz, Z = {:>.1f} @1MHz, {:>.1f} @10MHz, {:>.1f} @100MHz'.format(
            bdata.name,
            eng_fmt(bdata.L(1e6)),
            eng_fmt(bdata.xpoint(), '.2'),
            max_z,
            eng_fmt(max_z_freq, '.1'),
            abs(bdata.z(1e6)),
            abs(bdata.z(10e6)),
            abs(bdata.z(100e6)))
        )

