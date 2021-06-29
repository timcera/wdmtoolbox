.. include:: ../BADGES.rst
Usage - Command Line
====================
Just run 'wdmtoolbox' to get a list of subcommands

.. program-output:: wdmtoolbox --help

The default for all of the subcommands that accept time-series data is to pull
from stdin (typically a pipe or redirection).  If a subcommand accepts an input file for an
argument, you can use "... --input_ts=input_file_name.csv ...", or redirection
"... < input_file_name.csv".

A WDM file stores time-series asociated with a Data Set Number (DSN).  A DSN is
a number between 1 and 32000, though HSPF can only use for input and output
DSNs below 1000.  DSN numbers of 1000 and above should be used for
calculation and observed time-series.  The DSN must exist before before being
used.

Typical usage::

    wdmtoolbox createnewwdm met.wdm

    wdmtoolbox createnewdsn met.wdm 101 --tcode=3 --constituent=HPCP --tstype=HPCP --location=12345678 --description='NWS STATION 1' --scenario=INPUT

    wdmtoolbox csvtowdm met.wdm 1011 < nws_station_1.csv

To look at the DSN table::

    wdmtoolbox listdsns met.wdm

You can also use "tsgettoolbox" to populate the DSN with data from various
on-line sources.  Look at the "tsgettoolbox" documentation at
:ref:`tsgettoolbox_documentation` for particulars on installation, but it may
be as easy as "pip install tsgettoolbox".

"tsgettoolbox" examples::

    # Make a new wdm.
    wdmtoolbox createnewwdm obs.wdm

    # Create new DSN.
    wdmtoolbox createnewdsn obs.wdm 10 --scenario SIMULATE --location 02232000 --constituent FLOW

    # Download flow data for USGS station 02232000 and pipe into DSN.
    # The --startDT option is required otherwise only the latest value is
    # returned.
    tsgettoolbox nwis --sites=02232000 --parameterCd=00060 --startDT 2000-01-01 | wdmtoolbox csvtowdm obs.wdm 10

    # List DSNs.
    wdmtoolbox listdsns obs.wdm

    # Plot the flow data in DSN 10.
    wdmtoolbox extract obs.wdm 10 | tstoolbox plot

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

extract
~~~~~~~
.. program-output:: wdmtoolbox extract --help

wdmtostd
~~~~~~~~
.. program-output:: wdmtoolbox wdmtostd --help

wdmtoswmm5rdii
~~~~~~~~~~~~~~
.. program-output:: wdmtoolbox wdmtoswmm5rdii --help


Usage - API
===========
You can use all of the command line subcommands as functions.  The function
signature is identical to the command line subcommands.

Returns:

* wdmtoolbox.extract returns a PANDAS DataFrame.
* wdmtoolbox.listdsns returns a Python dictionary.
* Almost all of the remaining functions do not return anything.

Input can be a CSV or TAB separated file, or a
PANDAS DataFrame and is supplied to the function via the 'input_ts' keyword.

Simply import wdmtoolbox::

    from wdmtoolbox import wdmtoolbox

    # Then you could call the functions
    ntsd = wdmtoolbox.extract('test.wdm', 4)

    # Once you have a PANDAS DataFrame you can use that as input.
    # For example, use 'tstoolbox' to aggregate...
    from tstoolbox import tstoolbox
    ntsd = tstoolbox.aggregate(statistic='mean', agg_interval='daily', input_ts=ntsd)
