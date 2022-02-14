# -*- coding: utf-8 -*-
"""The component functions of the wdmtoolbox.

Used to manipulate Watershed Data Management files for time-series.
"""
from __future__ import print_function

import datetime
import os
import sys

# Third party imports
from builtins import range, str
from collections import OrderedDict

import mando
import numpy as np
import pandas as pd
from dateutil.parser import parse as dateparser
from mando.rst_text_formatter import RSTHelpFormatter

# Local imports
# Load in WDM subroutines
from tstoolbox import tsutils

from . import wdmutil

WDM = wdmutil.WDM()


def _describedsn(wdmpath, dsn):
    """Private function used by routines that need a description of DSN."""
    return WDM.describe_dsn(wdmpath, int(dsn))


def _copy_dsn(inwdmpath, indsn, outwdmpath, outdsn):
    """Copy a DSN label and data."""
    _copy_dsn_label(inwdmpath, indsn, outwdmpath, outdsn)
    nts = WDM.read_dsn(inwdmpath, indsn)
    if len(nts) > 0:
        WDM.write_dsn(outwdmpath, int(outdsn), nts)


def _copy_dsn_label(inwdmpath, indsn, outwdmpath, outdsn):
    """Copy a DSN label."""
    WDM.copydsnlabel(inwdmpath, indsn, outwdmpath, outdsn)


def _copydsn_core(inwdmpath, indsn, outwdmpath, outdsn, func, overwrite=False):
    if overwrite is True:
        deletedsn(outwdmpath, outdsn)
    if inwdmpath == outwdmpath:
        import tempfile

        tempdir = tempfile.mkdtemp()
        tmpwdmpath = os.path.join(tempdir, "temp.wdm")
        createnewwdm(tmpwdmpath)
        func(inwdmpath, indsn, tmpwdmpath, outdsn)
        func(tmpwdmpath, outdsn, outwdmpath, outdsn)
        os.remove(tmpwdmpath)
        os.removedirs(tempdir)
    else:
        func(inwdmpath, indsn, outwdmpath, outdsn)


@mando.command(formatter_class=RSTHelpFormatter, doctype="numpy")
@tsutils.doc(tsutils.docstrings)
def copydsnlabel(inwdmpath, indsn, outwdmpath, outdsn, overwrite=False):
    """Make a copy of a DSN label (no data).

    Parameters
    ----------
    inwdmpath
        Path to input WDM
        file.
    indsn
        Source
        DSN.
    outwdmpath
        Path to clean copy WDM
        file.
    outdsn
        Target
        DSN.
    overwrite
        Whether to overwrite the target DSN if it
        exists.

    """
    _copydsn_core(
        inwdmpath, indsn, outwdmpath, outdsn, _copy_dsn_label, overwrite=False
    )


@mando.command(formatter_class=RSTHelpFormatter, doctype="numpy")
@tsutils.doc(tsutils.docstrings)
def copydsn(inwdmpath, indsn, outwdmpath, outdsn, overwrite=False):
    """Make a copy of a DSN.

    Parameters
    ----------
    inwdmpath
        Path to input WDM
        file.
    indsn
        Source
        DSN.
    outwdmpath
        Path to clean copy WDM
        file.
    outdsn
        Target
        DSN.
    overwrite
        Whether to overwrite the target DSN if it
        exists.

    """
    _copydsn_core(inwdmpath, indsn, outwdmpath, outdsn, _copy_dsn, overwrite=False)


@mando.command(formatter_class=RSTHelpFormatter, doctype="numpy")
@tsutils.doc(tsutils.docstrings)
def cleancopywdm(inwdmpath, outwdmpath, overwrite=False):
    """Make a clean copy of a WDM file.

    Parameters
    ----------
    inwdmpath
        Path to input WDM
        file.
    outwdmpath
        Path to clean copy WDM
        file.
    overwrite
        Whether to overwrite an existing
        outwdmpath.

    """
    if inwdmpath == outwdmpath:
        raise ValueError(
            tsutils.error_wrapper(
                """
The "inwdmpath" cannot be the same as "outwdmpath".
"""
            )
        )
    createnewwdm(outwdmpath, overwrite=overwrite)
    activedsn = []
    for i in range(1, 32000):
        try:
            activedsn.append(_describedsn(inwdmpath, i)["dsn"])
        except wdmutil.WDMError:
            continue
    # Copy labels (which copies DSN metadata and data)
    for i in activedsn:
        try:
            _copy_dsn(inwdmpath, i, outwdmpath, i)
        except wdmutil.WDMError:
            pass


@mando.command(formatter_class=RSTHelpFormatter, doctype="numpy")
@tsutils.doc(tsutils.docstrings)
def renumberdsn(wdmpath, olddsn, newdsn):
    """Renumber olddsn to newdsn.

    Parameters
    ----------
    wdmpath : str
        Path and WDM
        filename.
    olddsn : int
        Old DSN to
        renumber.
    newdsn : int
        New DSN to change old DSN
        to.

    """
    WDM.renumber_dsn(wdmpath, olddsn, newdsn)


@mando.command(formatter_class=RSTHelpFormatter, doctype="numpy")
@tsutils.doc(tsutils.docstrings)
def deletedsn(wdmpath, dsn):
    """Delete DSN.

    Parameters
    ----------
    wdmpath
        Path and WDM
        filename.
    dsn
        DSN to
        delete.

    """
    WDM.delete_dsn(wdmpath, dsn)


@mando.command(formatter_class=RSTHelpFormatter, doctype="numpy")
@tsutils.doc(tsutils.docstrings)
def wdmtoswmm5rdii(wdmpath, *dsns, **kwds):
    """Print out DSN data to the screen in SWMM5 RDII format.

    Parameters
    ----------
    wdmpath
        Path and WDM
        filename.
    dsns
        The Data Set Numbers in the WDM
        file.
    kwds
        Current supported keywords are "start_date" and
        "end_date".

    """
    start_date = kwds.setdefault("start_date", None)
    end_date = kwds.setdefault("end_date", None)

    # Need to make sure that all DSNs are the same interval and all are
    # within start and end dates.
    collect_tcodes = {}
    collect_tsteps = {}
    collect_keys = []
    for dsn in dsns:
        dsn_desc = _describedsn(wdmpath, dsn)
        collect_tcodes[dsn_desc["tcode"]] = 1
        collect_tsteps[dsn_desc["tstep"]] = 1
        if start_date:
            assert dateparser(start_date) >= dateparser(dsn_desc["start_date"])
        if end_date:
            assert dateparser(end_date) <= dateparser(dsn_desc["end_date"])
        collect_keys.append((dsn_desc["dsn"], dsn_desc["location"]))
    assert len(collect_tcodes) == 1
    assert len(collect_tsteps) == 1

    collect_tcodes = list(collect_tcodes.keys())[0]
    collect_tsteps = list(collect_tsteps.keys())[0]

    collected_start_dates = []
    collected_end_dates = []
    collected_ts = {}
    for dsn, location in collect_keys:
        tmp = WDM.read_dsn(wdmpath, int(dsn), start_date=start_date, end_date=end_date)
        collected_start_dates.append(tmp.index[0])
        collected_end_dates.append(tmp.index[-1])
        collected_ts[(dsn, location)] = tmp.values

    maptcode = {1: 1, 2: 60, 3: 3600, 4: 86400}

    print("SWMM5")
    print("RDII dump of DSNS {} from {}".format(dsns, wdmpath))
    print(maptcode[collect_tcodes] * collect_tsteps)
    print(1)
    print("FLOW CFS")
    print(len(dsns))
    for dsn, location in collect_keys:
        print("{}_{}".format(dsn, location))
    print("Node Year Mon Day Hr Min Sec Flow")
    # Can pick any time series because they should all have the same interval
    # and start and end dates.
    for dex, date in enumerate(tmp.index):
        for dsn, location in collect_keys:
            print(
                "{}_{} {} {:02} {:02} {:02} {:02} {:02} {}".format(
                    dsn,
                    location,
                    date.year,
                    date.month,
                    date.day,
                    date.hour,
                    date.minute,
                    date.second,
                    collected_ts[(dsn, location)][dex],
                )
            )


def extract(*wdmpath, **kwds):
    """Print out DSN data to the screen with ISO-8601 dates.

    This is the API version also used by 'extract_cli'
    """
    # Adapt to both forms of presenting wdm files and DSNs
    # Old form '... file.wdm 101 102 103 ...'
    # New form '... file.wdm,101 adifferentfile.wdm,101 ...
    try:
        start_date = kwds.pop("start_date")
    except KeyError:
        start_date = None
    try:
        end_date = kwds.pop("end_date")
    except KeyError:
        end_date = None
    if len(kwds) > 0:
        raise ValueError(
            tsutils.error_wrapper(
                """
The only allowed keywords are start_date and end_date.  You
have given {}.
""".format(
                    kwds
                )
            )
        )

    labels = []
    for lab in wdmpath:
        if "," in str(lab):
            labels.append(lab.split(","))
        else:
            if lab == wdmpath[0]:
                continue
            labels.append([wdmpath[0], lab])

    result = pd.DataFrame()
    cnt = 0
    for ind, lab in enumerate(labels):
        wdmpath = lab[0]
        dsn = lab[1]
        nts = WDM.read_dsn(wdmpath, int(dsn), start_date=start_date, end_date=end_date)
        if nts.columns[0] in result.columns:
            cnt = cnt + 1
            nts.columns = ["{}_{}".format(nts.columns[0], cnt)]
        result = result.join(nts, how="outer")
    return tsutils.asbestfreq(result)


@mando.command("extract", formatter_class=RSTHelpFormatter, doctype="numpy")
@tsutils.doc(tsutils.docstrings)
def extract_cli(start_date=None, end_date=None, *wdmpath):
    """Print out DSN data to the screen with ISO-8601 dates.

    Parameters
    ----------
    wdmpath
        Path and WDM filename followed by space separated list of
        DSNs. For example::

            'file.wdm 234 345 456'

            OR
            `wdmpath` can be space separated sets of 'wdmpath,dsn'.

            'file.wdm,101 file2.wdm,104 file.wdm,227'

    ${start_date}

    ${end_date}

    """
    return tsutils._printiso(
        extract(*wdmpath, start_date=start_date, end_date=end_date)
    )


@mando.command(formatter_class=RSTHelpFormatter, doctype="numpy")
@tsutils.doc(tsutils.docstrings)
def wdmtostd(wdmpath, *dsns, **kwds):  # start_date=None, end_date=None):
    """DEPRECATED: New scripts use 'extract'. Will be removed in the future."""
    return extract(wdmpath, *dsns, **kwds)


@mando.command(formatter_class=RSTHelpFormatter, doctype="numpy")
@tsutils.doc(tsutils.docstrings)
def describedsn(wdmpath, dsn):
    """Print out a description of a single DSN.

    Parameters
    ----------
    wdmpath
        Path and WDM
        filename.
    dsn
        The Data Set Number in the WDM
        file.

    """
    print(_describedsn(wdmpath, dsn))


@mando.command("listdsns", formatter_class=RSTHelpFormatter, doctype="numpy")
@tsutils.doc(tsutils.docstrings)
def listdsns_cli(wdmpath):
    """Print out a table describing all DSNs in the WDM.

    Parameters
    ----------
    wdmpath
        Path and WDM
        filename.

    """
    nvars = listdsns(wdmpath)
    collect = OrderedDict()
    for _, testv in nvars.items():
        for key in [
            "DSN",
            "SCENARIO",
            "LOCATION",
            "CONSTITUENT",
            "TSTYPE",
            "START_DATE",
            "END_DATE",
            "TCODE",
            "TSTEP",
        ]:
            collect.setdefault(key, []).append(testv[key.lower()])
    return tsutils._printiso(collect, tablefmt="plain")


def listdsns(wdmpath):
    """Print out a table describing all DSNs in the WDM."""
    if not os.path.exists(wdmpath):
        raise ValueError(
            tsutils.error_wrapper(
                """
File {} does not exist.
""".format(
                    wdmpath
                )
            )
        )

    collect = OrderedDict()
    for i in range(1, 32001):
        try:
            testv = _describedsn(wdmpath, i)
        except wdmutil.WDMError:
            continue
        collect[i] = testv
    return collect


@mando.command(formatter_class=RSTHelpFormatter, doctype="numpy")
@tsutils.doc(tsutils.docstrings)
def createnewwdm(wdmpath, overwrite=False):
    """Create a new WDM file, optional to overwrite.

    Parameters
    ----------
    wdmpath
        Path and WDM
        filename.
    overwrite
        Defaults to not overwrite existing
        file.

    """
    WDM.create_new_wdm(wdmpath, overwrite=overwrite)


@mando.command(formatter_class=RSTHelpFormatter, doctype="numpy")
@tsutils.doc(tsutils.docstrings)
def createnewdsn(
    wdmpath,
    dsn,
    tstype="",
    base_year=1900,
    tcode=4,
    tsstep=1,
    statid="",
    scenario="",
    location="",
    description="",
    constituent="",
    tsfill=-999.0,
):
    """Create a new DSN.

    Parameters
    ----------
    wdmpath
        Path and WDM filename.  HSPF is limited to a path
        and WDM file name of 64 characters.  'wdmtoolbox' is
        only limited by the command line limits.

    dsn
        The Data Set Number in the WDM file.  This number
        must be greater or equal to 1 and less than or equal
        to 32000.  HSPF can only use for input or output
        DSNs of 1 to 9999, inclusive.

    tstype
        Time series type.  Can be any 4 character string, but if not
        specified defaults to first 4 characters of 'constituent'.  Must
        match what is used in HSPF UCI file.

        Limited to 4 characters.

    base_year
        Base year of time series, defaults to 1900.  The DSN will not
        accept any time-stamps before this date.

    tcode
        Time series code, (1=second, 2=minute, 3=hour, 4=day, 5=month,
        6=year) defaults to 4=daily.

    tsstep
        Time series steps, defaults (and almost always is)
        1.

    statid
        The station name, defaults to
        ''.

        Limited to 16 characters.

    scenario
        The name of the scenario, defaults to ''.  Can be anything, but
        typically, 'OBSERVED' for calibration and input time-series and
        'SIMULATE' for HSPF results.

        Limited to 8 characters.

    location
        The location, defaults to
        ''.

        Limited to 8 characters.

    description
        Descriptive text, defaults to
        ''.

        Limited to 48 characters.

    constituent
        The constituent that the time series represents, defaults to
        ''.

        Limited to 8 characters.

    tsfill
        The value used as placeholder for missing
        values.

    """
    if tstype == "" and len(constituent) > 0:
        tstype = constituent[:4]
    WDM.create_new_dsn(
        wdmpath,
        int(dsn),
        tstype=tstype,
        base_year=base_year,
        tcode=tcode,
        tsstep=tsstep,
        statid=statid,
        scenario=scenario,
        location=location,
        description=description,
        constituent=constituent,
        tsfill=tsfill,
    )


@mando.command(formatter_class=RSTHelpFormatter, doctype="numpy")
@tsutils.doc(tsutils.docstrings)
def hydhrseqtowdm(wdmpath, dsn, input_ts=sys.stdin, start_century=1900):
    """Write HYDHR sequential file to a DSN.

    Parameters
    ----------
    wdmpath
        Path and WDM
        filename.
    dsn
        The Data Set Number in the WDM
        file.
    input_ts
        Input filename, defaults to standard
        input.
    start_century
        Since 2 digit years are used, need century, defaults
        to 1900.

    """
    import pandas as pd

    dsn = int(dsn)
    if isinstance(input_ts, str):
        input_ts = open(input_ts, "r")
    dates = np.array([])
    data = np.array([])
    for line in input_ts:
        words = line[8:]
        words = words.split()
        year = int(words[0]) + start_century
        month = int(words[1])
        day = int(words[2])
        ampmflag = int(words[3])
        if int(words[0]) == 99 and month == 12 and day == 31 and ampmflag == 2:
            start_century = start_century + 100
        data = np.append(data, [float(i) for i in words[4:16]])
        try:
            if ampmflag == 1:
                dates = np.append(
                    dates,
                    [datetime.datetime(year, month, day, i) for i in range(0, 12)],
                )
            if ampmflag == 2:
                dates = np.append(
                    dates,
                    [datetime.datetime(year, month, day, i) for i in range(12, 24)],
                )
        except ValueError:
            print(start_century, line)
    data = pd.DataFrame(data, index=dates)
    _writetodsn(wdmpath, dsn, data)


@mando.command(formatter_class=RSTHelpFormatter)
@tsutils.doc(tsutils.docstrings)
def stdtowdm(wdmpath, dsn, infile="-"):
    """DEPRECATED: Use 'csvtowdm'."""
    csvtowdm(wdmpath, dsn, input_ts=infile)


@mando.command(formatter_class=RSTHelpFormatter, doctype="numpy")
@tsutils.doc(tsutils.docstrings)
def csvtowdm(
    wdmpath,
    dsn,
    start_date=None,
    end_date=None,
    columns=None,
    force_freq=None,
    groupby=None,
    round_index=None,
    clean=False,
    target_units=None,
    source_units=None,
    input_ts="-",
):
    """Write data from a CSV file to a DSN.

    File can have comma separated
    'year', 'month', 'day', 'hour', 'minute', 'second', 'value'
    OR
    'date/time string', 'value'

    Parameters
    ----------
    wdmpath
        Path and WDM
        filename.
    dsn
        The Data Set Number in the WDM
        file.
    ${input_ts}
    ${start_date}
    ${end_date}
    ${columns}
    ${force_freq}
    ${groupby}
    ${round_index}
    ${clean}
    ${target_units}
    ${source_units}
    """
    tsd = tsutils.common_kwds(
        input_ts,
        start_date=start_date,
        end_date=end_date,
        pick=columns,
        force_freq=force_freq,
        groupby=groupby,
        round_index=round_index,
        clean=clean,
        target_units=target_units,
        source_units=source_units,
    )

    if len(tsd.columns) > 1:
        raise ValueError(
            tsutils.error_wrapper(
                """
The input data set must contain only 1 time series.
You gave {}.
""".format(
                    len(tsd.columns)
                )
            )
        )

    _writetodsn(wdmpath, dsn, tsd)


def _writetodsn(wdmpath, dsn, data):
    """Local function to write Pandas data frame to DSN."""
    data = tsutils.asbestfreq(data)
    infer = data.index.freqstr
    pandacode = infer.lstrip("0123456789")
    tstep = infer[: infer.find(pandacode)]
    try:
        tstep = int(tstep)
    except ValueError:
        tstep = 1

    invmapcode = {
        1: "second",
        2: "minute",
        3: "hour",
        4: "day",
        5: "month",
        6: "annual",
    }

    mapcode = {
        "A": 6,  # annual
        "A-DEC": 6,  # annual
        "AS": 6,  # annual start
        "M": 5,  # month
        "MS": 5,  # month start
        "D": 4,  # day
        "H": 3,  # hour
        "T": 2,  # minute
        "S": 1,  # second
    }
    try:
        finterval = mapcode[pandacode]
    except KeyError:
        raise KeyError(
            """
*
*   wdmtoolbox only understands PANDAS time intervals of :
*   'A', 'AS', 'A-DEC' for annual,
*   'M', 'MS' for monthly,
*   'D', 'H', 'T', 'S' for day, hour, minute, and second.
*   wdmtoolbox thinks this series is {}.
*
""".format(
                pandacode
            )
        )

    # Convert string to int
    dsn = int(dsn)

    # Make sure that input data metadata matches target DSN
    desc_dsn = _describedsn(wdmpath, dsn)

    dsntcode = desc_dsn["tcode"]
    if finterval != dsntcode:
        raise ValueError(
            tsutils.error_wrapper(
                """
The DSN {2} has a tcode of {0} ({3}),
but the data has a tcode of {1} ({4}).
""".format(
                    dsntcode,
                    finterval,
                    dsn,
                    invmapcode[dsntcode],
                    invmapcode[finterval],
                )
            )
        )

    dsntstep = desc_dsn["tstep"]
    if dsntstep != tstep:
        raise ValueError(
            tsutils.error_wrapper(
                """
The DSN has a tstep of {}, but the data has a tstep of {}.
""".format(
                    dsntstep, tstep
                )
            )
        )

    WDM.write_dsn(wdmpath, dsn, data)


def main():
    """Run the main function."""
    if not os.path.exists("debug_wdmtoolbox"):
        sys.tracebacklimit = 0
    mando.main()


if __name__ == "__main__":
    main()
