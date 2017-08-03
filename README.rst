.. image:: https://travis-ci.org/timcera/wdmtoolbox.svg?branch=master
    :target: https://travis-ci.org/timcera/wdmtoolbox
    :height: 20

.. image:: https://coveralls.io/repos/timcera/wdmtoolbox/badge.png?branch=master
    :target: https://coveralls.io/r/timcera/wdmtoolbox?branch=master
    :height: 20

.. image:: https://img.shields.io/pypi/v/wdmtoolbox.svg
    :alt: Latest release
    :target: https://pypi.python.org/pypi/wdmtoolbox

.. image:: http://img.shields.io/badge/license-BSD-lightgrey.svg
    :alt: wdmtoolbox license
    :target: https://pypi.python.org/pypi/wdmtoolbox/

The wdmtoolbox
==============
The `wdmtoolbox` is a Python script and library to read/write/manage Watershed
Data Management (WDM) files used for time-series in hydrology and hydrological
simulation.  WDM files are used in the Hydrological Simulation Program -
FORTRAN (HSPF) and the Better Assessment of Science Integrating point and Non-point Sources (BASINS).  HSPF is a part of the BASINS system.

EPA BASINS - (http://water.epa.gov/scitech/datait/models/basins/)

Aqua Terra, BASINS download - (http://ftp.hspf.com/)

Requirements
============
If these requirements are not locally available, 'pip' or 'easy_install' will
attempt to download and install.

* pandas - on Windows this is part of the Python(x,y) distribution
  (http://code.google.com/p/pythonxy/) or Anaconda
  (https://store.continuum.io/cshop/anaconda/)

* baker - command line parser

* python-dateutil - used for parsing date/time strings

* tstoolbox - a command line utility companion to `wdmtoolbox`.

If you use the source distribution you have to have a FORTRAN compiler
installed and configured for your environment.

Installation for the Impatient
==============================

Compile From Source
-------------------
Aside from using pre-compiled binaries on Windows, the following command needs
gcc, gfortran, and probably want the Python science stack already installed.  
::

        pip install wdmtoolbox


