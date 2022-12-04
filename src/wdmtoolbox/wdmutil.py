"""Utilities to work with WDM files.

The WDM class supplies a series of utilities for working with WDM files
with Python.  The class uses f2py to wrap the minimally necessary WDM
routines.
"""


import datetime
import os
import os.path
import re

import _wdm_lib
import numpy as np
import pandas as pd
from filelock import SoftFileLock
from toolbox_utils import tsutils

# Mapping between WDM TCODE and pandas interval code
# Somewhere in the distant past, these slightly diverged - don't remember the
# reason.
_MAPTCODE = {1: "S", 2: "T", 3: "H", 4: "D", 5: "MS", 6: "AS"}
_MAPECODE = {1: "S", 2: "T", 3: "H", 4: "D", 5: "M", 6: "A"}
_NOTPRESENT = "<Not present on dataset>"

_attrib_alias = {
    "LOCATION": "IDLOCN",
    "SCENARIO": "IDSCEN",
    "CONSTITUENT": "IDCONS",
    "TSTEP": "TSSTEP",
    "START_DATE": "start_date",
    "END_DATE": "end_date",
}


class WDMError(Exception):
    """The default Error class."""


class DSNDoesNotExist(Exception):
    """The Error class if DSN does no exist."""

    def __init__(self, dsn):
        """Initialize DSN number."""
        self.dsn = dsn

    def __str__(self):
        """Print detailed error message."""
        if self.dsn < 1 or self.dsn > 32000:
            return f"""
*
*   The DSN number must be >= 1 and <= 32000.
*   You supplied {self.dsn}.
*
"""

        return f"""
*
*   The DSN {self.dsn} does not exist in the dataset.
*
"""


class WDMFileExists(Exception):
    """Error class if WDM file exist."""

    def __init__(self, filename):
        """Initialize filename."""
        self.filename = filename

    def __str__(self):
        """Return detailed error message."""
        return f"""
*
*   File {self.filename} exists.
*
"""


class DSNExistsError(Exception):
    """Error class if DSN exist."""

    def __init__(self, dsn):
        """Initialize DSN."""
        self.dsn = dsn

    def __str__(self):
        """Return detailed error message."""
        return f"""
*
*   DSN {self.dsn} exists.
*
"""


class WDM:
    """Class to open and read from WDM files."""

    def __init__(self):
        """Set functions from WDM library to class function objects."""
        # timcvt: Convert times to account for 24 hour
        # timdif: Time difference
        # wdmopn: Open WDM file
        # wdsagy: Get attribute metadata
        # wdbsac: Set string attribute
        # wdbsai: Set integer attribute
        # wdbsar: Set real attribute
        # wdbsgc: Get string attribute
        # wdbsgi: Get integer attribute
        # wdbsgr: Get real attribute
        # wdbsgx: Check attribute by name
        # wdbckt: Check if DSN exists
        # wdflcl: Close WDM file
        # wdlbax: Create label for new DSN
        # wdtget: Get time-series data
        # wdtput: Write time-series data
        # wddsrn: Renumber a DSN
        # wddsdl: Delete a DSN
        # wddscl: Copy a label

        self.timcvt = _wdm_lib.timcvt
        self.timdif = _wdm_lib.timdif
        self.wdbopn = _wdm_lib.wdbopn
        self.wdsagy = _wdm_lib.wdsagy
        self.wdbsac = _wdm_lib.wdbsac
        self.wdbsai = _wdm_lib.wdbsai
        self.wdbsar = _wdm_lib.wdbsar
        self.wdbsgc = _wdm_lib.wdbsgc
        self.wdbsgi = _wdm_lib.wdbsgi
        self.wdbsgr = _wdm_lib.wdbsgr
        self.wdbsgx = _wdm_lib.wdbsgx
        self.wdckdt = _wdm_lib.wdckdt
        self.wdflcl = _wdm_lib.wdflcl
        self.wdlbax = _wdm_lib.wdlbax
        self.wdtget = _wdm_lib.wdtget
        self.wdtput = _wdm_lib.wdtput
        self.wtfndt = _wdm_lib.wtfndt
        self.wddsrn = _wdm_lib.wddsrn
        self.wddsdl = _wdm_lib.wddsdl
        self.wddscl = _wdm_lib.wddscl

        self.openfiles = {}

    def wmsgop(self):
        """WMSGOP is a simple open of the message file."""
        afilename = os.path.join(os.path.dirname(__file__), "message.wdm")
        return self._open(afilename, 50, ronwfg=1)

    def dateconverter(self, datestr):
        """Extract and convert dates.

        Extract all of the grouped numbers out of a string
        to create an array suitable for dates and times.
        """
        words = re.findall(r"\d+", str(datestr))
        words = [int(i) for i in words]
        dtime = [1900, 1, 1, 0, 0, 0]
        dtime[: len(words)] = words
        return np.array(dtime)

    def _open(self, wdname, wdmsfl, ronwfg=0):
        """Private method to open WDM file."""
        wdname = wdname.strip()
        if wdname not in self.openfiles:
            if ronwfg in (0, 1) and not os.path.exists(wdname):
                raise ValueError(
                    tsutils.error_wrapper(
                        f"""
                        Trying to open file "{wdname}" and it cannot be found.
                        """
                    )
                )
            retcode = self.wdbopn(wdmsfl, wdname, ronwfg)
            self._retcode_check(retcode, additional_info=f"wdbopn file={wdname} DSN=NA")
            self.openfiles[wdname] = wdmsfl
        return wdmsfl

    def _retcode_check(self, retcode, additional_info=" "):
        """Central place to run through the return code."""
        if retcode == 0:
            return
        retcode_dict = {
            -1: "non specific error on WDM file open",
            -4: """copy/update failed due to data overlap problem - part of
    source needed""",
            -5: "copy/update failed due to data overlap problem",
            -6: "no data present",
            -8: "bad dates",
            -9: "data present in current group",
            -10: "no date in this group",
            -11: "no non-missing data, data has not started yet",
            -14: "data specified not within valid range for data set",
            -15: """time units and time step must match label exactly with
    VBTIME = 1""",
            -20: """problem with one or more of
    GPGLG, DXX, NVAL, QUALVL, Ltsstep, LTUNIT""",
            -21: "data from WDM does not match expected date",
            -23: "not a valid table",
            -24: "not a valid associated table",
            -25: "template already exists",
            -26: "can not add another table",
            -27: "no tables to return info about",
            -28: "table does not exist yet",
            -30: "more than whole table",
            -31: "more than whole extension",
            -32: "data header does not match",
            -33: "problems with row/space specs",
            -36: "missing needed following data for a get",
            -37: "no data present",
            -38: "missing part of time required",
            -39: "missing data group",
            -40: "no data available",
            -41: "no data to read",
            -42: "overlap in existing group",
            -43: "can not add another space time group",
            -44: "trying to get/put more data that in block",
            -45: "types do not match",
            -46: "bad space time group specification parameter",
            -47: "bad direction flag",
            -48: "conflicting spec of space time dim and # of ts data sets",
            -49: "group does not exist",
            -50: "requested attributes missing from this data set",
            -51: "no space for another DLG",
            -61: "old data set does not exist",
            -62: "new data set already exists",
            -71: "data set already exists",
            -72: "old data set does not exist",
            -73: "new data set already exists",
            -81: "data set does not exist",
            -82: "data set exists, but is wrong DSTYP",
            -83: "WDM file already open, can not create it",
            -84: "data set number out of valid range",
            -85: "trying to write to a read-only data set",
            -87: "can not remove message WDM file from buffer",
            -88: "can not open another WDM file",
            -89: "check digit on 1st record of WDM file is bad",
            -101: "incorrect character value for attribute",
            -102: "attribute already on label",
            -103: "no room on label for attribute",
            -104: "data present, can not update attribute",
            -105: "attribute not allowed for this type data set",
            -106: "can not delete attribute, it is required",
            -107: "attribute not present on this data set",
            -108: "incorrect integer value for attribute",
            -109: "incorrect real value for attribute",
            -110: "attributes not found on message file",
            -111: "attribute name not found (no match)",
            -112: "more attributes exists which match SAFNAM",
            -121: "no space for another attribute",
            1: "varies - generally more data/groups/table",
            2: "no more data available for this DLG group",
        }

        if retcode in retcode_dict:
            lopenfiles = self.openfiles.copy()
            for ofn in lopenfiles:
                self._close(ofn)
            raise WDMError(
                tsutils.error_wrapper(
                    f"""
                    WDM library function returned error code {retcode}.
                    {additional_info} WDM error: {retcode_dict[retcode]}
                    """
                )
            )
        if retcode != 0:
            for ofn in list(self.openfiles):
                self._close(ofn)
            raise WDMError(
                tsutils.error_wrapper(
                    f"""
                    WDM library function returned error code {retcode}.
                    {additional_info}
                    """
                )
            )

    def renumber_dsn(self, wdmpath, odsn, ndsn):
        """Will renumber the odsn to the ndsn."""
        odsn = int(odsn)
        ndsn = int(ndsn)

        lock = SoftFileLock(wdmpath + ".lock", timeout=30)
        with lock:
            wdmfp = self._open(wdmpath, 51)
            retcode = self.wddsrn(wdmfp, odsn, ndsn)
            self._close(wdmpath)
        self._retcode_check(
            retcode, additional_info=f"wddsrn file={wdmpath} DSN={odsn}"
        )

    def delete_dsn(self, wdmpath, dsn):
        """Delete a DSN."""
        dsn = int(dsn)

        lock = SoftFileLock(wdmpath + ".lock", timeout=30)
        with lock:
            wdmfp = self._open(wdmpath, 52)
            testreturn = self.wdckdt(wdmfp, dsn)
            self._close(wdmpath)
            if testreturn != 0:
                wdmfp = self._open(wdmpath, 52)
                retcode = self.wddsdl(wdmfp, dsn)
                self._close(wdmpath)
                self._retcode_check(
                    retcode, additional_info=f"wddsdl file={wdmpath} DSN={dsn}"
                )

            self._close(wdmpath)

    def copydsnlabel(self, inwdmpath, indsn, outwdmpath, outdsn):
        """Will copy a complete DSN label from one DSN to another."""
        assert inwdmpath != outwdmpath
        indsn = int(indsn)
        outdsn = int(outdsn)
        dsntype = 0
        inwdmfp = self._open(inwdmpath, 53, ronwfg=1)
        lock = SoftFileLock(outwdmpath + ".lock", timeout=30)
        with lock:
            outwdmfp = self._open(outwdmpath, 54)
            retcode = self.wddscl(inwdmfp, indsn, outwdmfp, outdsn, dsntype)
            self._close(outwdmpath)
        self._close(inwdmpath)
        self._retcode_check(
            retcode, additional_info=f"wddscl file={inwdmpath} DSN={indsn}"
        )

    def describe_dsn(self, wdmpath, dsn, attrs="default"):
        """Will collect some metadata about the DSN, including attributes and
        time span of data."""
        wdmfp = self._open(wdmpath, 55, ronwfg=1)
        _, llsdat, lledat, retcode = self.wtfndt(
            wdmfp, dsn, 1
        )  # GPFLG  - get(1)/put(2) flag
        self._close(wdmpath)
        # Ignore retcode == -6 which means that the DSN doesn't have any data.
        # If it is a new DSN, of course it doesn't have any data.
        if retcode == -6:
            retcode = 0
        self._retcode_check(retcode, additional_info=f"wtfndt file={wdmpath} DSN={dsn}")

        # format start and end dates
        self.timcvt(llsdat)
        self.timcvt(lledat)
        try:
            sdate = datetime.datetime(*llsdat).date()
        except ValueError:
            sdate = None
        try:
            edate = datetime.datetime(*lledat).date()
        except ValueError:
            edate = None

        messfp = self.wmsgop()
        if attrs == "default":
            attrib_list = [33, 17, 32, 290, 288, 289, 27, 45, 1]
        elif attrs == "all":
            attrib_list = list(range(1, 450))
        else:
            attrib_name_list = tsutils.make_list(attrs)
            attrib_list = []
            for name in attrib_name_list:
                name = _attrib_alias.get(name.upper(), name)
                if len(name) > 6:
                    raise ValueError(
                        tsutils.error_wrapper(
                            f"""{name} is too long - attribute names are
                            6 characters or less.
                            """
                        )
                    )
                name = name[:6].ljust(6).upper()
                attrib_index, attrib_type, attrib_len = self.wdbsgx(messfp, name)
                if attrib_index <= 0:
                    raise ValueError(
                        tsutils.error_wrapper(f"{name} is not a valid attribute name")
                    )
                attrib_list.append(attrib_index)
        wdmfp = self._open(wdmpath, 55, ronwfg=1)
        attrib_dict = {"DSN": dsn}
        for index in attrib_list:
            (
                name,
                _,  # data pointer
                attrib_type,
                attrib_len,
                _,  # attribute usage
                _,  # attribute update
            ) = self.wdsagy(messfp, index)
            attrib_name = b"".join(name).strip().decode("ascii")
            if not attrib_name:
                continue
            if attrib_type == 1:
                attrib_ival, retcode = self.wdbsgi(
                    wdmfp,
                    dsn,
                    index,
                    attrib_len,
                )
                if retcode == 0:
                    attrib_dict[attrib_name] = attrib_ival[0]
            elif attrib_type == 2:
                attrib_rval, retcode = self.wdbsgr(
                    wdmfp,
                    dsn,
                    index,
                    attrib_len,
                )
                if retcode == 0:
                    attrib_dict[attrib_name] = attrib_rval[0]
            elif attrib_type == 3:
                attrib_cval, retcode = self.wdbsgc(
                    wdmfp,
                    dsn,
                    index,
                    attrib_len,
                )
                if retcode == 0:
                    attrib_cval = b"".join(attrib_cval).strip().decode("ascii")
                    attrib_dict[attrib_name] = attrib_cval
            if retcode == -107 and attrs != "all":
                attrib_dict[attrib_name] = _NOTPRESENT
                retcode = 0
        self._close(wdmpath)

        try:
            tcode = attrib_dict["TCODE"]
            attrib_dict["tcode_name"] = _MAPTCODE[tcode]
            attrib_dict["start_date"] = pd.Period(sdate, freq=_MAPECODE[tcode])
            attrib_dict["end_date"] = pd.Period(edate, freq=_MAPECODE[tcode])
            attrib_dict["llsdat"] = llsdat
            attrib_dict["lledat"] = lledat
        except KeyError:
            tcode = -999
        return attrib_dict

    def create_new_wdm(self, wdmpath, overwrite=False):
        """Create a new WDM fileronwfg."""
        if overwrite and os.path.exists(wdmpath):
            self._close(wdmpath)
            os.remove(wdmpath)
        elif os.path.exists(wdmpath):
            raise WDMFileExists(wdmpath)
        ronwfg = 2
        self._open(wdmpath, 56, ronwfg=ronwfg)
        self._close(wdmpath)

    def set_attribute(self, wdmpath, dsn, attrib_name, attrib_val):
        """Set attribute of the DSN."""
        wdmfp = self._open(wdmpath, 60)
        messfp = self.wmsgop()

        name = attrib_name.ljust(6).upper()
        name = _attrib_alias.get(name, name)
        attrib_index, attrib_type, attrib_len = self.wdbsgx(messfp, name)

        if attrib_type == 0:
            raise ValueError(
                tsutils.error_wrapper(f"No attribute called {attrib_name}.")
            )

        if attrib_type == 1:
            val = int(attrib_val)
            retcode = self.wdbsai(wdmfp, dsn, messfp, attrib_index, attrib_len, val)
        elif attrib_type == 2:
            val = float(attrib_val)
            retcode = self.wdbsar(wdmfp, dsn, messfp, attrib_index, attrib_len, val)
        elif attrib_type == 3:
            val = attrib_val.strip()
            val = f"{val: <{attrib_len}}"
            retcode = self.wdbsac(wdmfp, dsn, messfp, attrib_index, attrib_len, val)
        self._retcode_check(
            retcode,
            additional_info=f"set_attributes file={wdmpath} DSN={dsn}, attribu_name={attrib_name}",
        )

    def create_new_dsn(
        self,
        wdmpath,
        dsn,
        tstype="",
        base_year=1900,
        tcode=4,
        tsstep=1,
        statid=" ",
        scenario="",
        location="",
        description="",
        constituent="",
        tsfill=-999.0,
    ):
        """Create self.wdmfp/dsn."""
        lock = SoftFileLock(wdmpath + ".lock", timeout=30)
        with lock:
            wdmfp = self._open(wdmpath, 57)
            messfp = self.wmsgop()

            if self.wdckdt(wdmfp, dsn) == 1:
                self._close(wdmpath)
                raise DSNExistsError(dsn)

            # Parameters for wdlbax taken from ATCTSfile/clsTSerWDM.cls
            self.wdlbax(
                wdmfp,
                dsn,
                1,  # DSTYPE - always 1 for time series
                10,  # NDN    - number of down pointers
                10,  # NUP    - number of up pointers
                30,  # NSA    - number of search attributes
                100,  # NSASP  - amount of search attribute space
                300,  # NDP    - number of data pointers
            )  # PSA    - pointer to search attribute space

            for saind, salen, saval in (
                (34, 1, 6),  # tgroup
                (83, 1, 1),  # compfg
                (84, 1, 1),  # tsform
                (85, 1, 1),  # vbtime
                (17, 1, int(tcode)),  # tcode
                (33, 1, int(tsstep)),  # tsstep
                (27, 1, int(base_year)),  # tsbyr
            ):
                retcode = self.wdbsai(wdmfp, dsn, messfp, saind, salen, saval)
                if retcode != 0:
                    self.delete_dsn(wdmfp, dsn)
                self._retcode_check(
                    retcode, additional_info=f"wdbsai file={wdmpath} DSN={dsn}"
                )

            for saind, salen, saval in ((32, 1, tsfill),):  # tsfill
                retcode = self.wdbsar(wdmfp, dsn, messfp, saind, salen, saval)
                if retcode != 0:
                    self.delete_dsn(wdmfp, dsn)
                self._retcode_check(
                    retcode, additional_info=f"wdbsar file={wdmpath} DSN={dsn}"
                )

            for saind, salen, saval, error_name in (
                (2, 16, statid, "Station ID"),
                (1, 4, tstype, "Time series type - tstype"),
                (45, 48, description, "Description"),
                (288, 8, scenario, "Scenario"),
                (289, 8, constituent, "Constituent"),
                (290, 8, location, "Location"),
            ):
                saval = saval.strip()
                if len(saval) > salen:
                    self.delete_dsn(wdmfp, dsn)
                    raise ValueError(
                        tsutils.error_wrapper(
                            f"""
                            String "{saval}" is too long for {error_name}.
                            Must have a length equal or less than {salen}.
                            """
                        )
                    )

                saval = f"{saval: <{salen}}"

                retcode = self.wdbsac(wdmfp, dsn, messfp, saind, salen, saval)
                if retcode != 0:
                    self.delete_dsn(wdmfp, dsn)
                self._retcode_check(
                    retcode, additional_info=f"wdbsac file={wdmpath} DSN={dsn}"
                )

            self._close(wdmpath)

    def _tcode_date(self, tcode, date):
        """Use tcode to set the significant parts of the date tuple."""
        rdate = [1, 1, 1, 0, 0, 0]
        if tcode <= 6:
            rdate[0] = date[0]
        if tcode <= 5:
            rdate[1] = date[1]
        if tcode <= 4:
            rdate[2] = date[2]
        if tcode <= 3:
            rdate[3] = date[3]
        if tcode <= 2:
            rdate[4] = date[4]
        if tcode <= 1:
            rdate[5] = date[5]
        return rdate

    def write_dsn(self, wdmpath, dsn, data):
        """Write to self.wdmfp/dsn the time-series data."""
        desc_dsn = self.describe_dsn(
            wdmpath, dsn, attrs=["TCODE", "TSSTEP", "TSFILL", "TSBYR"]
        )
        tcode = desc_dsn["TCODE"]
        tsstep = desc_dsn["TSSTEP"]
        tsfill = desc_dsn["TSFILL"]
        tsbyr = desc_dsn["TSBYR"]

        data.fillna(tsfill, inplace=True)
        start_date = data.index[0]

        dstart_date = start_date.timetuple()[:6]
        llsdat = self._tcode_date(tcode, dstart_date)
        if tsbyr > llsdat[0]:
            raise ValueError(
                tsutils.error_wrapper(
                    f"""
                    The base year for this DSN is {tsbyr}.  All data to insert
                    must be after the base year.  Instead the first year of the
                    series is {llsdat[0]}.
                    """
                )
            )

        nval = len(data)
        lock = SoftFileLock(wdmpath + ".lock", timeout=30)
        with lock:
            wdmfp = self._open(wdmpath, 58)
            retcode = self.wdtput(wdmfp, dsn, tsstep, llsdat, nval, 1, 0, tcode, data)
            self._close(wdmpath)
        self._retcode_check(retcode, additional_info=f"wdtput file={wdmpath} DSN={dsn}")

    def read_dsn(self, wdmpath, dsn, start_date=None, end_date=None):
        """Read from a DSN."""
        if not os.path.exists(wdmpath):
            raise ValueError(
                tsutils.error_wrapper(
                    f"""
                    File {wdmpath} does not exist.
                    """
                )
            )

        # Call wdatim_ to get TSSTEP, TCODE, TSFILL
        desc_dsn = self.describe_dsn(wdmpath, dsn, attrs=["TCODE", "TSSTEP", "TSFILL"])

        llsdat = desc_dsn["llsdat"]
        lledat = desc_dsn["lledat"]
        tcode = desc_dsn["TCODE"]
        tsstep = desc_dsn["TSSTEP"]
        tsfill = desc_dsn["TSFILL"]

        if tsfill == _NOTPRESENT:
            tsfill = -999

        # These calls convert 24 to midnight of the next day
        self.timcvt(llsdat)
        self.timcvt(lledat)

        if start_date is not None:
            start_date = self.dateconverter(start_date)
            start_date = datetime.datetime(*start_date)
            if start_date > datetime.datetime(*lledat):
                raise ValueError(
                    tsutils.error_wrapper(
                        f"""
                        The requested start date ({start_date}) is after the
                        end date ({datetime.datetime(*lledat)}) of the time
                        series in the WDM file.
                        """
                    )
                )

        if end_date is not None:
            end_date = self.dateconverter(end_date)
            end_date = datetime.datetime(*end_date)
            if end_date < datetime.datetime(*llsdat):
                raise ValueError(
                    tsutils.error_wrapper(
                        f"""
                        The requested end date ({end_date}) is before the start
                        date ({datetime.datetime(*llsdat)}) of the time series
                        in the WDM file.
                        """
                    )
                )

        iterm = self.timdif(llsdat, lledat, tcode, tsstep)

        dtran = 0
        qualfg = 30
        # Get the data and put it into dictionary
        wdmfp = self._open(wdmpath, 59, ronwfg=1)
        dataout, retcode = self.wdtget(
            wdmfp, dsn, tsstep, llsdat, iterm, dtran, qualfg, tcode
        )
        self._close(wdmpath)

        if len(dataout) == 0:
            return pd.DataFrame()

        self._retcode_check(retcode, additional_info=f"wdtget file={wdmpath} DSN={dsn}")

        index = pd.date_range(
            datetime.datetime(*llsdat),
            periods=iterm,
            freq=f"{tsstep:d}{_MAPTCODE[tcode]}",
        )

        # Convert time series to pandas DataFrame
        tmpval = pd.DataFrame(
            pd.Series(
                dataout, index=index, name=f"{os.path.basename(wdmpath)}_DSN_{dsn}"
            ),
            dtype=np.float64,
        )

        tmpval = tsutils.common_kwds(
            input_tsd=tmpval, start_date=start_date, end_date=end_date
        )
        tmpval.replace(tsfill, np.nan, inplace=True)
        tmpval.index.name = "Datetime"
        return tmpval

    def read_dsn_por(self, wdmpath, dsn):
        """Read the period of record for a DSN."""
        return self.read_dsn(wdmpath, dsn)

    def _close(self, wdmpath):
        """Close the WDM file."""
        wdmpath = wdmpath.strip()
        if wdmpath in self.openfiles:
            retcode = self.wdflcl(self.openfiles[wdmpath])
            self._retcode_check(
                retcode, additional_info=f"wdflcl file={wdmpath} DSN=NA"
            )
            self.openfiles.pop(wdmpath)


if __name__ == "__main__":
    wdm_obj = WDM()
    fname = r"c:\test.wdm" if os.name == "nt" else "test.wdm"
    wdm_obj.create_new_wdm(fname, overwrite=True)
    listonumbers = [34.2, 35.0, 36.9, 38.2, 40.2, 20.1, 18.4, 23.6]
    wdm_obj.create_new_dsn(
        fname, 1003, tstype="EXAM", scenario="OBSERVED", location="EXAMPLE"
    )
    dr = pd.date_range(start="2000-01-01", freq="D", periods=len(listonumbers))
    df = pd.DataFrame(listonumbers, index=dr)
    wdm_obj.write_dsn(fname, 1003, df)
    print(wdm_obj.read_dsn_por(fname, 1003))
