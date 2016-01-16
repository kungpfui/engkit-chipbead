#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# $Id$

"""Example code to find some matching chip ferrite beads."""

import beadselect

PARAM = dict(
    # 0201, 0402, 0603, 0805, 1206 (inch)
    size='0603',
    # |Z| @ 100MHz
    impedance=(270, 360),
    # optional, L @ 1MHz, just uncomment
    #~ inductance=(2e-6, 3e-6)
    )


def main():
    "let it run"
    data = beadselect.filescan(**PARAM)

    # informations goes to stdout
    beadselect.info(data)

    # graphical data to a window
    beadselect.plot(data, frange=(1e6, 1e9), rmin=1.0)


if __name__ == "__main__":
    main()
