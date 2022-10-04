"""The component functions of the wdmtoolbox.

Used to manipulate Watershed Data Management files for time-series.
"""


import datetime
import os
import sys
from collections import OrderedDict

import numpy as np
import pandas as pd
from cltoolbox import Program
from cltoolbox.rst_text_formatter import RSTHelpFormatter
from dateutil.parser import parse as dateparser
from tabulate import tabulate as tb
from toolbox_utils import tsutils

# Load in WDM subroutines
from . import wdmutil

program = Program("wdmtoolbox", 0.0)

_common_docs = {
    "wdmpath": r"""wdmpath: str
        Path and WDM
        filename.""",
    "inwdmpath": r"""inwdmpath: str
        Path and WDM filename of the input
        WDM file.""",
    "outwdmpath": r"""outwdmpath: str
        Path and WDM filename of the output
        WDM file.""",
    "dsn": r"""dsn: int
        The Data Set Number (DSN) for the time series in the WDM file.
        This number must be greater or equal to 1 and less than or
        equal to 32000.  HSPF can only use for input or output
        DSNs of 1 to 9999, inclusive.""",
    "indsn": r"""indsn: int
        Source
        DSN.""",
    "outwdmpath": r"""outwdmpath: str
        Path to clean copy WDM
        file.""",
    "outdsn": r"""outdsn: int
        Target
        DSN.""",
    "overwrite": r"""overwrite: bool
        Whether to overwrite the target DSN if it
        exists.""",
    "olddsn": r"""olddsn : int
        Old DSN to
        renumber.""",
    "newdsn": r"""newdsn : int
        New DSN to change old DSN
        to.""",
    "attrs": r"""attrs : str
        [optional, default to "default"]

        Attributes to retrieve from the DSN.

        +--------------------+---------------------------------------------+
        | attrs              | Attributes Retrieved                        |
        +====================+=============================================+
        | default            | DSN, TSSTEP, TCODE, TSFILL, IDLOCN, IDSCEN, |
        |                    | IDCONS, TSBYR, STANAM, TSTYPE               |
        +--------------------+---------------------------------------------+
        | all                | All attributes set of the 450 total         |
        +--------------------+---------------------------------------------+
        | comma separated    | Specific attributes named in the list       |
        | list of attribute  |                                             |
        | names              |                                             |
        +--------------------+---------------------------------------------+
    """,
    "tstype": r"""tstype: str
        [optional, default to first 4 characters of 'constituent']

        Time series type.  Can be any 4 character string, but if not
        specified defaults to first 4 characters of 'constituent'.  Must
        match what is used in HSPF UCI file.

        Limited to 4 characters.""",
    "base_year": r"""base_year: int
        [optional, defaults to 1900]

        Base year of time series.  The DSN will not
        accept any time-series before this date and with the default settings
        of TGROUP=6 (i.e. yearly) would allow time-series up to 2199.""",
    "tcode": r"""tcode: int
        [optional, defaults to 4=daily time series]

        Time series code, (1=second, 2=minute, 3=hour, 4=day, 5=month,
        6=year)""",
    "tsstep": r"""tsstep: int
        [optional, defaults to 1]

        Time series steps, defaults (and almost always is)
        1.""",
    "statid": r"""statid: str
        [optional, defaults to '']

        The station name, limited to 16 characters.""",
    "scenario": r"""scenario: str
        [optional defaults to '']

        The name of the scenario.  Can be anything, but
        typically, 'OBSERVED' for calibration and input time-series and
        'SIMULATE' for model results.

        Limited to 8 characters.""",
    "location": r"""location: str
        [optional defaults to '']

        The location name.

        Limited to 8 characters.""",
    "description": r"""description: str
        [optional, defaults to '']

        Descriptive text.

        Limited to 48 characters.""",
    "constituent": r"""constituent: str
        [optional, defaults to '']

        The constituent that the time series represents.

        Limited to 8 characters.""",
    "tsfill": r"""tsfill: int
        [optional, defaults to -999]

        A time-series in a WDM file must have a value for every time interval.
        The "tsfill" number is used as a placeholder for missing values.

        Change to a number that is guaranteed to not be a valid number in your
        time-series.""",
}

_common_docs.update(tsutils.docstrings)

WDM = wdmutil.WDM()


def describedsn(wdmpath, dsn, attrs="default"):
    """Private function used by routines that need a description of DSN."""
    return WDM.describe_dsn(wdmpath, int(dsn), attrs)


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


@program.command(formatter_class=RSTHelpFormatter)
@tsutils.doc(_common_docs)
def copydsnlabel(inwdmpath, indsn, outwdmpath, outdsn, overwrite=False):
    r"""Make a copy of a DSN label (no data).

    Parameters
    ----------
    ${inwdmpath}
    ${indsn}
    ${outwdmpath}
    ${outdsn}
    ${overwrite}

    """
    _copydsn_core(
        inwdmpath, indsn, outwdmpath, outdsn, _copy_dsn_label, overwrite=False
    )


@program.command(formatter_class=RSTHelpFormatter)
@tsutils.doc(_common_docs)
def copydsn(inwdmpath, indsn, outwdmpath, outdsn, overwrite=False):
    """Make a copy of a DSN.

    Parameters
    ----------
    ${inwdmpath}
    ${indsn}
    ${outwdmpath}
    ${outdsn}
    ${overwrite}

    """
    _copydsn_core(inwdmpath, indsn, outwdmpath, outdsn, _copy_dsn, overwrite=False)


@program.command(formatter_class=RSTHelpFormatter)
@tsutils.doc(_common_docs)
def cleancopywdm(inwdmpath, outwdmpath, overwrite=False):
    """Make a clean copy of a WDM file.

    Parameters
    ----------
    ${inwdmpath}
    ${outwdmpath}
    ${overwrite}

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
            activedsn.append(describedsn(inwdmpath, i)["DSN"])
        except wdmutil.WDMError:
            continue
    # Copy labels (which copies DSN metadata and data)
    for i in activedsn:
        try:
            _copy_dsn(inwdmpath, i, outwdmpath, i)
        except wdmutil.WDMError:
            pass


@program.command(formatter_class=RSTHelpFormatter)
@tsutils.doc(_common_docs)
def renumberdsn(wdmpath, olddsn, newdsn):
    """Renumber olddsn to newdsn.

    Parameters
    ----------
    ${wdmpath}
    ${olddsn}
    ${newdsn}

    """
    WDM.renumber_dsn(wdmpath, olddsn, newdsn)


@program.command(formatter_class=RSTHelpFormatter)
@tsutils.doc(_common_docs)
def deletedsn(wdmpath, dsn):
    """Delete DSN.

    Parameters
    ----------
    ${wdmpath}
    dsn
        DSN to
        delete.

    """
    WDM.delete_dsn(wdmpath, dsn)


@program.command(formatter_class=RSTHelpFormatter)
@tsutils.doc(_common_docs)
def wdmtoswmm5rdii(wdmpath, *dsns, **kwds):
    """Print out DSN data to the screen in SWMM5 RDII format.

    Parameters
    ----------
    ${wdmpath}
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
    collect_tssteps = {}
    collect_keys = []
    for dsn in dsns:
        desc_dsn = describedsn(wdmpath, dsn, attrs=["TCODE", "TSSTEP", "IDLOCN"])
        collect_tcodes[desc_dsn["TCODE"]] = 1
        collect_tssteps[desc_dsn["TSSTEP"]] = 1
        if start_date:
            assert dateparser(start_date) >= dateparser(desc_dsn["start_date"])
        if end_date:
            assert dateparser(end_date) <= dateparser(desc_dsn["end_date"])
        collect_keys.append((desc_dsn["DSN"], desc_dsn["IDLOCN"]))
    assert len(collect_tcodes) == 1
    assert len(collect_tssteps) == 1

    collect_tcodes = list(collect_tcodes.keys())[0]
    collect_tssteps = list(collect_tssteps.keys())[0]

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
    print(f"RDII dump of DSNS {dsns} from {wdmpath}")
    print(maptcode[collect_tcodes] * collect_tssteps)
    print(1)
    print("FLOW CFS")
    print(len(dsns))
    for dsn, location in collect_keys:
        print(f"{dsn}_{location}")
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
            try:
                labels.append(lab.split(","))
            except AttributeError:
                labels.append(lab)
        elif lab != wdmpath[0]:
            labels.append([wdmpath[0], lab])

    result = pd.DataFrame()
    cnt = 0
    for lab in labels:
        wdmpath, dsn = lab
        nts = WDM.read_dsn(wdmpath, int(dsn), start_date=start_date, end_date=end_date)
        if nts.columns[0] in result.columns:
            cnt = cnt + 1
            nts.columns = [f"{nts.columns[0]}_{cnt}"]
        result = result.join(nts, how="outer")
    return tsutils.asbestfreq(result)


@program.command("extract", formatter_class=RSTHelpFormatter)
@tsutils.doc(_common_docs)
def extract_cli(start_date=None, end_date=None, *wdmpath):
    """Print out DSN data to the screen with ISO-8601 dates.

    Parameters
    ----------
    ${wdmpath}
        followed by space separated list of
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


@program.command(formatter_class=RSTHelpFormatter)
def wdmtostd(wdmpath, *dsns, **kwds):  # start_date=None, end_date=None):
    """DEPRECATED: New scripts use 'extract'. Will be removed in the future."""
    return extract(wdmpath, *dsns, **kwds)


@program.command("describedsn", formatter_class=RSTHelpFormatter)
@tsutils.doc(_common_docs)
def describedsn_cli(wdmpath, dsn, attrs="default", tablefmt="dict"):
    """Print out attributes of a single DSN

    Parameters
    ----------
    ${wdmpath}
    ${dsn}
    ${attrs}
    ${tablefmt}

    """
    if tablefmt != "dict":
        attrib_dict = describedsn(wdmpath, dsn, attrs)
        attrib_df = pd.DataFrame.transpose(pd.DataFrame([attrib_dict]))
        attrib_table = tb(
            attrib_df,
            tablefmt=tablefmt,
            showindex="always",
            headers=["Attribute", "Value"],
        )
        print(attrib_table)
    else:
        print(describedsn(wdmpath, dsn, attrs))


@program.command("listdsns", formatter_class=RSTHelpFormatter)
@tsutils.doc(_common_docs)
def listdsns_cli(wdmpath):
    """Print out a table describing all DSNs in the WDM.

    Parameters
    ----------
    ${wdmpath}

    """
    nvars = listdsns(wdmpath)
    collect = OrderedDict()
    alias_attrib = {v: k for k, v in wdmutil._attrib_alias.items()}
    for _, testv in nvars.items():
        for key in [
            "DSN",
            "IDSCEN",
            "IDLOCN",
            "IDCONS",
            "TSTYPE",
            "start_date",
            "end_date",
            "TCODE",
            "TSSTEP",
        ]:
            nkey = alias_attrib.get(key, key)
            collect.setdefault(nkey, []).append(testv[key])
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
            testv = describedsn(wdmpath, i)
        except wdmutil.WDMError:
            continue
        collect[i] = testv
    return collect


@program.command(formatter_class=RSTHelpFormatter)
@tsutils.doc(_common_docs)
def createnewwdm(wdmpath, overwrite=False):
    """Create a new WDM file, optional to overwrite.

    Parameters
    ----------
    ${wdmpath}
    ${overwrite}

    """
    WDM.create_new_wdm(wdmpath, overwrite=overwrite)


@program.command(formatter_class=RSTHelpFormatter)
@tsutils.doc(_common_docs)
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
    ${wdmpath}
    ${dsn}
    ${tstype}
    ${base_year}
    ${tcode}
    ${tsstep}
    ${statid}
    ${scenario}
    ${location}
    ${description}
    ${constituent}
    ${tsfill}

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


@program.command(formatter_class=RSTHelpFormatter)
@tsutils.doc(_common_docs)
def hydhrseqtowdm(wdmpath, dsn, input_ts=sys.stdin, start_century=1900):
    """Write HYDHR sequential file to a DSN.

    Parameters
    ----------
    ${wdmpath}
    ${dsn}
    ${input_ts}
    start_century
        Since 2 digit years are used, need century, defaults
        to 1900.

    """
    import pandas as pd

    dsn = int(dsn)
    if isinstance(input_ts, str):
        input_ts = open(input_ts)
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
                    [datetime.datetime(year, month, day, i) for i in range(12)],
                )

            elif ampmflag == 2:
                dates = np.append(
                    dates,
                    [datetime.datetime(year, month, day, i) for i in range(12, 24)],
                )
        except ValueError:
            print(start_century, line)
    data = pd.DataFrame(data, index=dates)
    _writetodsn(wdmpath, dsn, data)


@program.command(formatter_class=RSTHelpFormatter)
def stdtowdm(wdmpath, dsn, infile="-"):
    """DEPRECATED: Use 'csvtowdm'."""
    csvtowdm(wdmpath, dsn, input_ts=infile)


@program.command(formatter_class=RSTHelpFormatter)
@tsutils.doc(_common_docs)
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
    ${wdmpath}
    ${dsn}
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
    tsstep = infer[: infer.find(pandacode)]
    try:
        tsstep = int(tsstep)
    except ValueError:
        tsstep = 1

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
    desc_dsn = describedsn(wdmpath, dsn)

    dsntcode = desc_dsn["TCODE"]
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

    dsntsstep = desc_dsn["TSSTEP"]
    if dsntsstep != tsstep:
        raise ValueError(
            tsutils.error_wrapper(
                """
The DSN has a tsstep of {}, but the data has a tsstep of {}.
""".format(
                    dsntsstep, tsstep
                )
            )
        )

    WDM.write_dsn(wdmpath, dsn, data)


@program.command(formatter_class=RSTHelpFormatter)
@tsutils.doc(_common_docs)
def setattrib(wdmpath, dsn, attrib_name, attrib_val):
    """Set an attribute value for the DSN.  See WDM documentation for full list of possible attributes and valid values.

    Parameters
    ----------
    ${wdmpath}
    ${dsn}
    attrib_name
        Six character name of attribute, or "Location", "Scenario",
        "Constituent"
    attrib_val
        Value for attribute.
        Must be correct type and a valid value.

    """
    WDM.set_attribute(wdmpath, int(dsn), attrib_name, attrib_val)


extract.__doc__ = extract_cli.__doc__
describedsn.__doc__ = describedsn_cli.__doc__
listdsns.__doc__ = listdsns_cli.__doc__


def main():
    """Run the main function."""
    if not os.path.exists("debug_wdmtoolbox"):
        sys.tracebacklimit = 0
    program()


if __name__ == "__main__":
    main()
