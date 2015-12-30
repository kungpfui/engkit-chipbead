pyBeadSelector
==============
a ferrite bead selector written in Python.

Ferrite beads are electronic components normally used for "noise" supression.
They work like inductors but there ferrite material is designed to be
lossy already at low frequencies.

The Problem
-----------
Sometimes I have to select ferrite beads for my electronic designs. Finding the right bead is a horrible task because the there are up to ten beads with equal impedance at the same frequency, size and supplied by the same manufacturer. Mostly each device has it's own datasheet and comparing, also against other manufacturers, becomes a nightmare.

Ok, luckily some vendors publish their scattering parameters as touchstone files
and even better you can get all files of a bead series as a single zip file. So there is not a lot of work to do to get the data. Why no using this collection and let the computer do a rough selection for you?


The Solution
------------
Luckily (again) I've worked with touchstone files in the past. I've used them to calculate some impedance matching networks at 2.4Ghz where the best real-world-part solution was determined by brute force.

I write such little tools always in [Python]. It's super easy, super quick written, super cheap and there are super libraries ... but you need some knowledge of this language.


The Files
---------
### beadparam.py
It's just a parameter setting file ... or an example how to use it.
#### How to use it?
Well, just setup your parameters. Size and impedance range must be specified.
Normally you get to many results with this to settings. So you can limit the result set even more by specifing an inductance range.

```python

param = dict(
    # 0201, 0402, 0603, 0805, 1206 (inch)
    size       = '0603',

    # |Z| @ 100MHz
    impedance  = (270, 360),

    # optional, L @ 1MHz
    #~ inductance = (1.8e-6, 2.5e-6)
)

```

### beadselect.py
Make sure you have downloaded the zip files with the s-parameter data from the manufacturer you like. At the moment there are four vendors supported. Of course you can add more. Just put the zip files into the same folder as the source files (I was very lazzy). These files must be registered within this Python file. Just look how it was done. Not so diffucult ... hopefully.

#### Supported Manufacturers
- [Murata]
- [TDK]
- [Tayo Yuden]
- [Würth]


### touchstone.py
A quick 'n' dirty touchstone file reader.
It's not proper done but should work most of the time.

The Result
----------
You got an output on stdout like this

```
BKP1608_HS271-T : L = 1.992uH, Z = 12.545 @1MHz, 103.107 @10MHz, 274.220 @100MHz
BLM18AG331SN1   : L = 2.193uH, Z = 13.789 @1MHz, 107.866 @10MHz, 353.747 @100MHz
MMZ1608R301ATA00: L = 2.387uH, Z = 15.013 @1MHz, 135.686 @10MHz, 286.299 @100MHz
BLM18EG331TN1   : L = 2.407uH, Z = 15.199 @1MHz, 106.453 @10MHz, 331.104 @100MHz
BLM18PG331SN1   : L = 2.473uH, Z = 15.605 @1MHz, 110.761 @10MHz, 341.590 @100MHz
```

and a graphical representation of the bead's data where |Z|, X and R are visible.

![Bead Selector Window][pyBeadSelector.png]


Notice
------
- [Python] 2.7 or 3.x needed.
- [Matplotlib] needed (pip install matplotlib).

If you are not familiar with [Python] a better starting point is [Anaconda].
[Anaconda] is Python with more scientific libraries installed already and therefore there are no installation hassles on windows systems.


[Murata]: http://www.murata.com/en-us/tool/sparameter/ferritebead/
[TDK]: https://product.tdk.com/info/en/technicalsupport/tvcl/general/beads.html
[Tayo Yuden]: http://www.yuden.co.jp/ut/product/support/pdf_spice_spara/
[Würth]: http://www.we-online.de/web/de/electronic_components/toolbox_pbs/S_Parameter_1.php
[Python]: http://www.python.org
[Matplotlib]: http://matplotlib.org/
[Anaconda]: https://www.continuum.io

[pyBeadSelector.png]: https://github.com/kungpfui/pyBeadSelector/blob/master/images/pyBeadSelector.png "Bead Selector Window"
