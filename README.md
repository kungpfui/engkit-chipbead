engkit-chipbead
===============
a ferrite chip bead selector written in the Python programming language.

Ferrite beads are electronic components normally used for "noise" suppression.
They work like inductors but there ferrite material is designed to be lossy
already at low frequencies. Some year ago, [INcompliance Magazine] has published
an article about this topic.

The Problem
-----------
Sometimes I have to select ferrite beads for my electronic designs. Finding the right
bead is a horrible task because there are up to ten beads with equal impedance at the same
frequency, size and supplied by the same manufacturer. Mostly each device has its own
datasheet and comparing, also against other manufacturers, becomes a nightmare.

Ok, luckily some vendors publish their scattering parameters as touchstone files
and even better you can get all files of a bead series as a single zip file. So there
is not a lot of work to do to get the data. Why no using this collection and let the
computer do a rough selection for you?

The Solution
------------
Luckily (again) I've worked with touchstone files in the past. I've used them to
calculate some impedance matching networks at 2.4Ghz where the best real-world-part
solution was determined by brute force.

The Files
---------

### examples/beadparam.py

It's just a parameter setting file ... or an example how to use it.

#### How to use it?

Well, just set up your parameters. Size and impedance range must be specified.
Normally you get too many results with this two settings. So you can limit the result set
even more by specifying an inductance range.

```python

param = dict(
    # 0201, 0402, 0603, 0805, 1206 (inch)
    size='0603',

    # |Z| @ 100MHz
    impedance=(270, 360),

    # optional, L @ 1MHz
    # inductance = (1.8e-6, 2.5e-6)
)

```

### ekbead/beadparts.py

Make sure you have downloaded the zip files with the s-parameter data from the
manufacturer you like. At the moment, there are four vendors supported. Of course,
you can add more. Just put the zip files into a *sparam* sub folder. These files
must be registered within this Python file. Just look how it was done. Not so
difficult ... hopefully.

#### Supported Manufacturers

- [Murata]
- [TDK]
- [Taiyo Yuden]
- [Würth]
- [Samsung] (semi-automatic)

This script can download the s-parameter files by themselves. Just execute and all
files are placed into the *sparam* folder (created if not exists). This should
have done automatically while setup.py runs.

### ekbead/beadselect.py

The visualisation stuff

### ekbead/touchstone.py

A quick 'n' dirty touchstone file reader.
It's not proper done but should work most of the time.

The Result
----------
You got an output on stdout like this

```
BKP1608_HS271-T     : L = 1.992uH, X=R @ 20.134MHz, Z = 12.55 @1MHz, 103.11 @10MHz, 274.22 @100MHz
BLM18AG331SN1       : L = 2.193uH, X=R @ 26.117MHz, Z = 13.79 @1MHz, 107.87 @10MHz, 353.75 @100MHz
MMZ1608R301ATA00    : L = 2.387uH, X=R @ 14.616MHz, Z = 15.01 @1MHz, 135.69 @10MHz, 286.30 @100MHz
BLM18EG331TN1       : L = 2.407uH, X=R @ 30.045MHz, Z = 15.20 @1MHz, 106.45 @10MHz, 331.10 @100MHz
BLM18PG331SN1       : L = 2.473uH, X=R @ 21.380MHz, Z = 15.61 @1MHz, 110.76 @10MHz, 341.59 @100MHz
```

and a graphical representation of the bead's data where |Z|, X and R are visible.

![Bead Selector Window][pyBeadSelector.png]


Notice
------

- [Python] ≥3.7 needed.

If you are not familiar with [Python] a better starting point is [Anaconda].
[Anaconda] is Python with much more installed scientific libraries and therefore there are no installation hassles on
Windows systems.


[INcompliance Magazine]: https://incompliancemag.com/article/all-ferrite-beads-are-not-created-equal-understanding-the-importance-of-ferrite-bead-material-behavior/

[Murata]: https://www.murata.com/en-us/tool/sparameter/ferritebead/

[TDK]: https://product.tdk.com/info/en/technicalsupport/tvcl/general/beads.html

[Taiyo Yuden]: https://www.yuden.co.jp/ut/product/support/pdf_spice_spara/

[Würth]: https://www.we-online.de/web/en/electronic_components/toolbox_pbs/S_Parameter_1.php

[Samsung]: https://weblib.samsungsem.com/LCR_Web_Library.jsp?type=bead&lng=en_US

[Python]: https://www.python.org

[Matplotlib]: https://matplotlib.org/

[Anaconda]: https://www.continuum.io

[pyBeadSelector.png]: https://github.com/kungpfui/engkit-chipbead/blob/master/images/pyBeadSelector.png "Bead Selector Window"
