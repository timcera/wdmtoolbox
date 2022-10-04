.. image:: https://github.com/timcera/wdmtoolbox/actions/workflows/python-package.yml/badge.svg
    :alt: Tests
    :target: https://github.com/timcera/wdmtoolbox/actions/workflows/python-package.yml
    :height: 20

.. image:: https://img.shields.io/coveralls/github/timcera/wdmtoolbox
    :alt: Test Coverage
    :target: https://coveralls.io/r/timcera/wdmtoolbox?branch=master
    :height: 20

.. image:: https://img.shields.io/pypi/v/wdmtoolbox.svg
    :alt: Latest release
    :target: https://pypi.python.org/pypi/wdmtoolbox/
    :height: 20

.. image:: https://img.shields.io/pypi/l/wdmtoolbox.svg
    :alt: BSD-3 clause license
    :target: https://pypi.python.org/pypi/wdmtoolbox/
    :height: 20

.. image:: https://img.shields.io/pypi/dd/wdmtoolbox.svg
    :alt: wdmtoolbox downloads
    :target: https://pypi.python.org/pypi/wdmtoolbox/
    :height: 20

.. image:: https://img.shields.io/pypi/pyversions/wdmtoolbox
    :alt: PyPI - Python Version
    :target: https://pypi.org/project/wdmtoolbox/
    :height: 20

wdmtoolbox
==========
The `wdmtoolbox` is a Python script and library to read/write/manage Watershed
Data Management (WDM) files used for time-series in hydrology and hydrological
simulation.  WDM files are used in the Hydrological Simulation Program -
FORTRAN (HSPF) and the Better Assessment of Science Integrating point and
Non-point Sources (BASINS).  HSPF is a part of the BASINS system.

BASINS, HSPF, and various utilities are available at
https://github.com/respec/BASINS/releases

For HSPF I also have developed:

* hspfbintoolbox to extract data from the HSPF binary output file
  https://timcera.bitbucket.io/hspfbintoolbox/docs/index.html
  install with `pip install hspfbintoolbox`
* hspf_utils to create water balance tables of the entire model, or particular
  years, and to create a CSV file useful to join to a GIS layer to map model
  results.
  https://timcera.bitbucket.io/hspf_utils/docs/index.html
  install with `pip install hspf_utils`

Installation for the Impatient
==============================
::

    pip install wdmtoolbox

For Windows should use the `conda` environment and install as many of the
required libraries with `conda install ...` before using `pip`..

Compile From Source
-------------------
To compile from source you need a "C" compiler (gcc on Linux, Visual Studio
2019 for Windows), a FORTRAN compiler (gfortran on Linux, MSYS2/MINGW gfortran
on Windows), Python 3.7, 3.8, or 3.9 with "numpy" installed to be able to access
`f2py`.

Additional Software
===================
https://timcera.bitbucket.io/index.html
