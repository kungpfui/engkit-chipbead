#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# $Id$

import beadselect

param = dict(
	# 0201, 0402, 0603, 0805, 1206 (inch)
	size       = '0603',

	# |Z| @ 100MHz
	impedance  = (270, 360),

	# optional, L @ 1MHz
	#~ inductance = (1.8e-6, 2.5e-6)
)


data = beadselect.filescan(**param)
beadselect.info(data)
beadselect.plot(data, frange=(1e6, 1e9), rmin=1.0)
