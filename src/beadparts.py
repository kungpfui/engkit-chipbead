#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# $Id$

import os
from collections import namedtuple

NameConv = namedtuple('NameConv', ['url', 'regex_fn','scmap'])

manufacturer = dict(
	murata     = NameConv('http://www.murata.com/~/media/webrenewal/tool/sparameter/ferritebeads/{filename_ext}.ashx?la=en-us',
	             r'.*(?P<size_code>\d{2})[A-Z]{2}(?P<imp_code>\d{3}).*',
	             {'0201' : '03', '0402' : '15', '0603' : '18', '0805' : '21', '1206' : '31'} ),

	tayo_yuden = NameConv('http://www.yuden.co.jp/productdata/spara/{filename}',
	             r'.*(?P<size_code>\d{4})_.*(?P<imp_code>\d{3}).*',
	             {'0402' : '1005', '0603' : '1608', '0805' : '2012'} ),

	tdk        = NameConv('https://product.tdk.com/info/tvcl/spara/{filename}',
	             r'.*(?P<size_code>\d{4})[A-Z](?P<imp_code>\d{3}).*',
	             {'0402' : '1005', '0603' : '1608', '0805' : '2012'} ),

	wuerth     = NameConv('http://www.we-online.de/web/en/index.php/download/media/07_electronic_components/download_center_1/s-parameter/{filename}',
	             r'^(?P<size_code>\d{7}).*',
	             {'0402' : '7427927', '0603' : '7427926', '0805' : '7427920'} ),
)

## subfolder to use for s-parameter zip files
folder = lambda f: os.path.join('sparam', f)

parts = {
	# murata parts, http://www.murata.com/en-us/tool/sparameter/ferritebead
	folder('blm15_s_v10.zip'): manufacturer['murata'],
	folder('blm18_s_v10.zip'): manufacturer['murata'],
	folder('blm21_s_v10.zip'): manufacturer['murata'],

	# TDK parts, https://product.tdk.com/info/en/technicalsupport/tvcl/general/beads.html
	folder('beads_commercial_signal_mmz1005_spara.zip'):   manufacturer['tdk'],
	folder('beads_commercial_signal_mmz1005-e_spara.zip'): manufacturer['tdk'],
	folder('beads_commercial_signal_mmz1005-v_spara.zip'): manufacturer['tdk'],
	folder('beads_commercial_power_mpz1005_spara.zip'):    manufacturer['tdk'],
	folder('beads_commercial_signal_mmz1608_spara.zip'):   manufacturer['tdk'],
	folder('beads_commercial_power_mpz1608_spara.zip'):    manufacturer['tdk'],
	folder('beads_commercial_signal_mmz2012_spara.zip'):   manufacturer['tdk'],
	folder('beads_commercial_power_mpz2012_spara.zip'):   manufacturer['tdk'],

	# Tayo Yuden parts, http://www.yuden.co.jp/ut/product/support/pdf_spice_spara/
	folder('BK.zip'):  manufacturer['tayo_yuden'],
	folder('BKP.zip'): manufacturer['tayo_yuden'],
	folder('FBM.zip'): manufacturer['tayo_yuden'],

	# Würth parts, http://www.we-online.de/web/en/electronic_components/toolbox_pbs/S_Parameter_1.php
	folder('WE_CBF_0402.zip'): manufacturer['wuerth'],
	folder('WE_CBF_0603.zip'): manufacturer['wuerth'],
	folder('WE_CBF_0805.zip'): manufacturer['wuerth'],
}



#------------------------------------------------------------------------------
def _simple_dl(url, filepath):
	with open(filepath, 'wb') as f:
		f.write( urlopen(url).read() )

def _get_sparam():
	""" download all missing s-parameter packages"""
	for fn in parts:
		if not parts[fn].url: continue

		if not os.path.exists(fn) or os.path.getsize(fn) == 0:
			if not os.path.exists(os.path.dirname(fn)): os.makedirs(os.path.dirname(fn))
			urlfmt = dict(filename=os.path.basename(fn),
				filename_ext=os.path.splitext(os.path.basename(fn))[0])
			try:
				print ("download '{}' ...".format(urlfmt['filename']))
				_simple_dl(parts[fn].url.format(**urlfmt), fn)
			except Exception as excptn:
				print ("error: {} @ '{}'".format(excptn, urlfmt['filename']))


if __name__ == "__main__":
	try:
		from urllib.request import urlopen
	except ImportError:
		from urllib import urlopen

	_get_sparam()
