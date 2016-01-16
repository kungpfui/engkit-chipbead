#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# $Id$

"""Example code to find some matching chip ferrite beads."""

import eekbead as bead

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
    data = bead.filescan(**PARAM)

    # informations goes to stdout
    bead.info(data)

    # graphical data to a window
    bead.plot(data, frange=(1e6, 1e9), rmin=1.0)


if __name__ == "__main__":
    main()
