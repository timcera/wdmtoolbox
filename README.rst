WDMTOOLBOX
==========
The wdmtoolbox is a Python script to read/write/manage Watershed Data
Management (WDM) files used for time-series in hydrology and hydrological
simulation.  

Requirements
============
* pandas - on Windows this is part of the Python(x,y) distribution
  (http://code.google.com/p/pythonxy/) or Anaconda
  (https://store.continuum.io/cshop/anaconda/)

* baker - command line parser

* python-dateutil - used for parsing date/time strings

If you use the source distribution you have to have a FORTRAN compiler
installed and configured for your environment.

Installation
============
Should be as easy as running ``easy_install wdmtoolbox`` or ``pip install
wdmtoolbox``` at any command line.  Not sure on Windows whether this will
bring in pandas but as mentioned above, if you start with Python(x,y) then
you won't have a problem.

The wdmtoolbox script is actually made up of two parts, 'wdmtoolbox' module
which handles all command line interaction and 'wdmutil.py' which is a library
of functions that 'wdmtoolbox' uses.  This means that you can write your
own scripts to access WDM files by importing the functionality from
'wdmutil.py'.

Running
=======
Just run 'wdmtoolbox' to get a list of subcommands::

    wdmtoolbox


If a subcommand accepts an input file for an arguement, you can use '-' to
indicate that the input is from a pipe.  For the subcommands that output data
it is printed to the screen and you can then redirect to a file.

API
===
All of the command-line subcommands are available as functions within Python
as methods associated with the wdmtoolbox.WDM() class.

Author
======

Tim Cera, P.E.

tim at cerazone dot net
