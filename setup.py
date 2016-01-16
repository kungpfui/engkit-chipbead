#!/usr/bin/env python

import os
import sys
from distutils.core import setup
from setuptools.command.install import install as _install

_package = 'ekbead'


class chipbead_data_install(_install):
    def run(self):
        _install.run(self)
        from subprocess import call
        call([sys.executable, 'beadparts.py'],
             cwd=self.install_lib + _package)


with open(os.path.join(_package, '__init__.py')) as fid:
    for line in fid:
        if line.startswith('__version__'):
            VERSION = line.strip().split()[-1][1:-1]
            break


LONG_DESCRIPTION = """
engkit-chipbead is an open source chip bead comparison and selection
tool implemented in the Python programming language.
"""

setup(name='engkit-chipbead',
    version=VERSION,
    author='Stefan Schwendeler',
    author_email='kungpfui@users.noreply.github.com',
    url='https://github.com/kungpfui/engkit-chipbead',
    description='SMD Chip Bead Selector',
    long_description=LONG_DESCRIPTION,
    license='GPL2.1',

    install_requires = [
        'numpy',
        'matplotlib',
        ],

    packages=[_package],

    cmdclass={'install': chipbead_data_install},

    )

