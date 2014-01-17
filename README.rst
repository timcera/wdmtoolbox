WDMTOOLBOX
==========
The wdmtoolbox is a Python script to read/write/manage Watershed Data
Management (WDM) files used for time-series in hydrology and hydrological
simulation.  

Requirements
============
If these requirements are not locally available, 'pip' or 'easy_install' will
attempt to download and install.

* pandas - on Windows this is part of the Python(x,y) distribution
  (http://code.google.com/p/pythonxy/) or Anaconda
  (https://store.continuum.io/cshop/anaconda/)

* baker - command line parser

* python-dateutil - used for parsing date/time strings

* tstoolbox - a command line utility companion to 'wdmtoolbox'.

If you use the source distribution you have to have a FORTRAN compiler
installed and configured for your environment.

Installation
============
On Windows should be as easy as running ``easy_install wdmtoolbox`` in a
command shell window.  On Linux (and maybe even Mac OSX?) you could use either
``pip install wdmtoolbox`` or ``easy_install wdmtoolbox`` at any terminal that
has access to gfortran and of course your Python interpreter.  Not sure on
Windows whether this will bring in pandas but as mentioned above, if you start
with Python(x,y) then you won't have a problem.

The wdmtoolbox script is actually made up of two parts, 'wdmtoolbox' module
which handles all command line interaction and 'wdmutil.py' which is a library
of functions that 'wdmtoolbox' uses.  This means that you can write your own
scripts to access WDM files by importing the functionality from 'wdmutil.py'.

Usage - Command Line
====================
Just run 'wdmtoolbox' to get a list of subcommands

.. program-output:: wdmtoolbox

The default for all of the subcommands that accept time-series data is to pull
from stdin (typically a pipe).  If a subcommand accepts an input file for an
argument, you can use "--input_ts=input_file_name.csv", or to explicitly
specify from stdin (the default) "--input_ts='-'".  

Sub-command Detail
''''''''''''''''''

cleancopywdm
~~~~~~~~~~~~
.. program-output:: wdmtoolbox cleancopywdm --help

copydsn
~~~~~~~
.. program-output:: wdmtoolbox copydsn --help

createnewdsn
~~~~~~~~~~~~
.. program-output:: wdmtoolbox createnewdsn --help

createnewwdm
~~~~~~~~~~~~
.. program-output:: wdmtoolbox createnewwdm --help

csvtowdm
~~~~~~~~
.. program-output:: wdmtoolbox csvtowdm --help

deletedsn
~~~~~~~~~
.. program-output:: wdmtoolbox deletedsn --help

describedsn
~~~~~~~~~~~
.. program-output:: wdmtoolbox describedsn --help

hydhrseqtowdm
~~~~~~~~~~~~~
.. program-output:: wdmtoolbox hydhrseqtowdm --help

listdsns
~~~~~~~~
.. program-output:: wdmtoolbox listdsns --help

renumberdsn
~~~~~~~~~~~
.. program-output:: wdmtoolbox renumberdsn --help

stdtowdm
~~~~~~~~
.. program-output:: wdmtoolbox stdtowdm --help

wdmtostd
~~~~~~~~
.. program-output:: wdmtoolbox wdmtostd --help

wdmtoswmm5rdii
~~~~~~~~~~~~~~
.. program-output:: wdmtoolbox wdmtoswmm5rdii --help


Usage - API
===========
You can use all of the command line subcommands as functions.  The function
signature is identical to the command line subcommands.  The return is always
a PANDAS DataFrame.  Input can be a CSV or TAB separated file, or a PANDAS
DataFrame and is supplied to the function via the 'input_ts' keyword.

Simply import wdmtoolbox::

    import wdmtoolbox

    # Then you could call the functions
    ntsd = wdmtoolbox.wdmtostd('test.wdm', 4)

    # Once you have a PANDAS DataFrame you can use that as input.
    # For example, use 'tstoolbox' to aggregate...
    import tstoolbox
    ntsd = tstoolbox.aggregate(statistic='mean', agg_interval='daily', input_ts=ntsd)

Author
======

Tim Cera, P.E.

tim at cerazone dot net
