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
