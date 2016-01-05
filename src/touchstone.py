#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# $Id$

import re
import cmath

class SPoint(object):
    """ Scattering paramter

        @f the frequency [Hz]
        @s the complex s-parameter (s11,s21,s12,s22)
        @s
    """

    def __init__(self, fmt, *args):
        """ c'tor
        @param fmt    TouchstoneFormat object
        @param args   list or tuple object with 3 or 9 float elements. Exact meaning
                      depends on @fmt.
                      The order is (f, s11, s11, s12, s12, s21, s21, s22, s22)
        """
        self.fmt = fmt

        # frequency
        self.f = self.fmt.fs * args[0]

        # value pairs (s11, s21, s12, s22)
        pair = self.fmt.convert
        self.s = tuple([pair(*arg)  for arg in zip(args[1::2], args[2::2])])

        # s1p or s2p file?
        self.ports = 1 if len(self.s) == 1 else 2
        self._z_term = 0.0 if self.ports == 1 else self.fmt.z0


    @property
    def Z(self):
        """ complex impedance of the element.

        The assumption is that the element was connetecd like 1 --@@@-- 2
        """
        # subtract the impedance of port 2 on 2-port measurements
        return self.Zin - self._z_term

    @property
    def L(self):
        """ inductance [H] of the elment.
        """
        return self.Z.imag / (cmath.pi * 2.0 * self.f)

    @property
    def Zin(self):
        gamma = (1.0 + self.s11) / (1.0 - self.s11)
        return gamma * self.fmt.z0

    @property
    def s11(self):
        return self.s[0]
    @property
    def s21(self):
        return self.s[1]
    @property
    def s12(self):
        return self.s[2]
    @property
    def s22(self):
        return self.s[3]


class TouchstoneFormat(object):
    mapping = (
        {'HZ':1.0, 'KHZ':1E3, 'MHZ':1E6, 'GHZ':1E9},
        # at the moment only s-parameters are supported (no Z, Y, ....)
        {'S':True},
        {
            # real-imaganyry, s11-re, s11-im, s21, s12, s22
            'RI':complex,
            # magnitude angle, |s11|, <s11, s21, s12, s22
            'MA':lambda magnitude, angle: cmath.rect(magnitude, angle * (cmath.pi / 180.0)),
            'DB':lambda magnitude, angle: cmath.rect(10.0**(magnitude/20.0), angle * (cmath.pi / 180.0)),
        },
        {'R':True},
        float
        )

    def __init__(self, sfmt):
        v = []
        for action, value in zip(self.mapping, sfmt):
            if isinstance(action, dict):
                v.append(action[value])
            elif callable(action):
                v.append(action(value))

        # frequency scaling
        self.fs = v[0]
        # must be true
        assert v[1]
        # the convertion function to use to convert into complex s-parameter
        self.convert = v[2]
        # must be true
        assert v[3]
        # the system impedance, normally 50+0j
        self.z0 = v[4]


class Touchstone(list):
    """ Quick n dirty touchstone file reader (.s2p only)
    """

    def __init__(self, fileobj):
        """c'tor
        @param fileobj 	file-like object
        """
        self.fileobj = fileobj
        self.s_option = None

    def _parse(self):
        """Parses the @fileobj
        @note the file is parsed only once.

        @ret list of SPoint objects
        """
        if self.s_option:
            return self

        if isinstance(self.fileobj, str):
            self.fileobj = open(self.fileobj, 'r')

        for line in self.fileobj:
            line = line.decode('latin-1').strip()
            if line:
                # a comment
                if line.startswith(('!')):
                    continue
                # an option
                if line.startswith(('#')):
                    self.s_option = TouchstoneFormat(line[1:].strip().upper().split())
                    continue
                # rest must/should be data
                line = re.sub(r'\s+', ' ', line)
                self.append(
                    SPoint(self.s_option, *(float(l) for l in line.split()))
                )
        self.fileobj.close()
        return self

    def __getitem__(self, idx):
        "get item by index"
        self._parse()
        return list.__getitem__(self, idx)

    def __iter__(self):
        "iterator"
        self._parse()
        return list.__iter__(self)

