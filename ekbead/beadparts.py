#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
List of ferrite chip beads.
"""

import os
from collections import namedtuple
try:
    from urllib.request import urlopen
except ImportError:
    # python 2.x
    from urllib import urlopen


## naming conventions of the manufacturer
NameConv = namedtuple('NameConv', ['url', 'regex_fn', 'scmap'])


MANUFACTURER = dict(
    murata=\
        NameConv('http://www.murata.com/~/media/webrenewal/tool/sparameter/ferritebeads/{filename_ext}.ashx?la=en-us',
                 r'.*(?P<size_code>\d{2})[A-Z]{2}(?P<imp_code>\d{3}).*',
                 {'0201': '03', '0402': '15', '0603': '18', '0805': '21', '1206': '31'}),
    #~ samsung=\
        #~ NameConv(None,
                 #~ r'.*(?P<size_code>\d{2})[A-Z](?P<imp_code>\d{3}).*',
                 #~ {'0603': '10'}),
    tayo_yuden=\
        NameConv('http://www.yuden.co.jp/productdata/spara/{filename}',
                 r'.*(?P<size_code>\d{4})_.*(?P<imp_code>\d{3}).*',
                 {'0402': '1005', '0603': '1608', '0805': '2012'}),
    tdk=\
        NameConv('https://product.tdk.com/info/tvcl/spara/{filename}',
                 r'.*(?P<size_code>\d{4})[A-Z](?P<imp_code>\d{3}).*',
                 {'0402': '1005', '0603': '1608', '0805': '2012'}),
    wuerth=\
        NameConv('http://www.we-online.de/web/en/index.php/download/media/07_electronic_components/download_center_1/s-parameter/{filename}',
                 r'^(?P<size_code>\d{7}).*',
                 {'0402': '7427927', '0603': '7427926', '0805': '7427920'}),
)



def _folder(zip_filename):
    """Subfolder to use for s-parameter zip files.
    @param zip_filename  filename as string, must be an existing zip-file
    """
    return os.path.join(os.path.dirname(__file__), 'sparam', zip_filename)


PARTS = {
    # murata parts, http://www.murata.com/en-us/tool/sparameter/ferritebead
    _folder('blm15_s_v10.zip'): MANUFACTURER['murata'],
    _folder('blm18_s_v10.zip'): MANUFACTURER['murata'],
    _folder('blm21_s_v10.zip'): MANUFACTURER['murata'],

    # TDK parts, https://product.tdk.com/info/en/technicalsupport/tvcl/general/beads.html
    _folder('beads_commercial_signal_mmz1005_spara.zip'):   MANUFACTURER['tdk'],
    _folder('beads_commercial_signal_mmz1005-e_spara.zip'): MANUFACTURER['tdk'],
    _folder('beads_commercial_signal_mmz1005-v_spara.zip'): MANUFACTURER['tdk'],
    _folder('beads_commercial_power_mpz1005_spara.zip'):    MANUFACTURER['tdk'],
    _folder('beads_commercial_signal_mmz1608_spara.zip'):   MANUFACTURER['tdk'],
    _folder('beads_commercial_power_mpz1608_spara.zip'):    MANUFACTURER['tdk'],
    _folder('beads_commercial_signal_mmz2012_spara.zip'):   MANUFACTURER['tdk'],
    _folder('beads_commercial_power_mpz2012_spara.zip'):   MANUFACTURER['tdk'],

    # Tayo Yuden parts, http://www.yuden.co.jp/ut/product/support/pdf_spice_spara/
    _folder('BK.zip'):  MANUFACTURER['tayo_yuden'],
    _folder('BKP.zip'): MANUFACTURER['tayo_yuden'],
    _folder('FBM.zip'): MANUFACTURER['tayo_yuden'],

    # Würth parts, http://www.we-online.de/web/en/electronic_components/toolbox_pbs/S_Parameter_1.php
    _folder('WE_CBF_0402.zip'): MANUFACTURER['wuerth'],
    _folder('WE_CBF_0603.zip'): MANUFACTURER['wuerth'],
    _folder('WE_CBF_0805.zip'): MANUFACTURER['wuerth'],

    # Samsung parts, http://weblib.samsungsem.com/LCR_Web_Library.jsp?type=bead&lng=en_US
    #~ _folder('CIM10_Series.zip'): MANUFACTURER['samsung'],
}



#------------------------------------------------------------------------------
def _simple_dl(url, filepath):
    """Very simple download function without excpetion handlers

    @param url       URL as string
    @param filepath  local filepath as string
    """
    with open(filepath, 'wb') as file_:
        file_.write(urlopen(url).read())


def _get_sparam():
    """Download all missing s-parameter packages.
    """
    for filepath in PARTS:
        if not PARTS[filepath].url:
            continue

        if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
            if not os.path.exists(os.path.dirname(filepath)):
                os.makedirs(os.path.dirname(filepath))
            urlfmt = dict(filename=os.path.basename(filepath),
                          filename_ext=os.path.splitext(os.path.basename(filepath))[0])
            try:
                print("download '{}' ...".format(urlfmt['filename']))
                _simple_dl(PARTS[filepath].url.format(**urlfmt), filepath)
            except Exception as excptn:
                print("error: {} @ '{}'".format(excptn, urlfmt['filename']))


if __name__ == "__main__":
    _get_sparam()
