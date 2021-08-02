# -*- coding: utf-8 -*-

"""
test_createnewdsn
----------------------------------

Tests for `tstoolbox` module.
"""

import os
import sys
import tempfile

try:
    from cStringIO import StringIO
except:
    from io import StringIO

from unittest import TestCase

from pandas.testing import assert_frame_equal
from tstoolbox import tstoolbox, tsutils

from wdmtoolbox import wdmtoolbox
from wdmtoolbox.wdmutil import WDMError


def capture(func, *args, **kwds):
    sys.stdout = StringIO()  # capture output
    out = func(*args, **kwds)
    out = sys.stdout.getvalue()  # release output
    try:
        out = bytes(out, "utf-8")
    except:
        pass
    return out


class TestDescribe(TestCase):
    def setUp(self):
        self.fd, self.wdmname = tempfile.mkstemp(suffix=".wdm")
        os.close(self.fd)
        self.test_dir = os.path.abspath(os.path.dirname(__file__))

    def tearDown(self):
        os.remove(self.wdmname)

    def test_tstep(self):
        wdmtoolbox.createnewwdm(self.wdmname, overwrite=True)
        wdmtoolbox.createnewdsn(self.wdmname, 101, tcode=2, base_year=1970, tsstep=15)
        wdmtoolbox.csvtowdm(
            self.wdmname,
            101,
            input_ts=os.path.join(self.test_dir, "nwisiv_02246000.csv"),
        )
        ret1 = wdmtoolbox.extract(self.wdmname, 101)
        ret2 = wdmtoolbox.extract("{},101".format(self.wdmname))
        assert_frame_equal(ret1, ret2, check_index_type=False)

        ret3 = tstoolbox.read(os.path.join(self.test_dir, "nwisiv_02246000.csv"))
        ret3.index = ret3.index.tz_localize(None)
        ret3 = tsutils.asbestfreq(ret3)
        ret1.columns = ["02246000_iv_00060"]
        assert_frame_equal(ret1, ret3, check_index_type=False)

    def test_extract_args(self):
        wdmtoolbox.createnewwdm(self.wdmname, overwrite=True)
        wdmtoolbox.createnewdsn(self.wdmname, 101, tcode=2, base_year=1970, tsstep=15)
        wdmtoolbox.csvtowdm(
            self.wdmname,
            101,
            input_ts=os.path.join(self.test_dir, "nwisiv_02246000.csv"),
        )
        with self.assertRaisesRegex(ValueError, "The only allowed keywords are"):
            ret1 = wdmtoolbox.extract(self.wdmname, 101, ph=True)

    def test_listdsns_verify(self):
        wdmtoolbox.createnewwdm(self.wdmname, overwrite=True)
        wdmtoolbox.createnewdsn(self.wdmname, 101, tcode=2, base_year=1970, tsstep=15)
        wdmtoolbox.csvtowdm(
            self.wdmname,
            101,
            input_ts=os.path.join(self.test_dir, "nwisiv_02246000.csv"),
        )
        ldsns = wdmtoolbox.listdsns(self.wdmname)

    def test_negative_dsn(self):
        wdmtoolbox.createnewwdm(self.wdmname, overwrite=True)
        wdmtoolbox.createnewdsn(self.wdmname, 101, tcode=2, base_year=1970, tsstep=15)
        wdmtoolbox.csvtowdm(
            self.wdmname,
            101,
            input_ts=os.path.join(self.test_dir, "nwisiv_02246000.csv"),
        )
        with self.assertRaisesRegex(
            WDMError, "WDM error: data set number out of valid range"
        ):
            ret1 = wdmtoolbox.extract(self.wdmname, 0)

    def test_out_of_bounds_dsn(self):
        wdmtoolbox.createnewwdm(self.wdmname, overwrite=True)
        wdmtoolbox.createnewdsn(self.wdmname, 101, tcode=2, base_year=1970, tsstep=15)
        wdmtoolbox.csvtowdm(
            self.wdmname,
            101,
            input_ts=os.path.join(self.test_dir, "nwisiv_02246000.csv"),
        )
        with self.assertRaisesRegex(
            WDMError, "WDM error: data set number out of valid range"
        ):
            ret1 = wdmtoolbox.extract(self.wdmname, 32001)

    def test_dsn_not_in_wdm(self):
        wdmtoolbox.createnewwdm(self.wdmname, overwrite=True)
        wdmtoolbox.createnewdsn(self.wdmname, 101, tcode=2, base_year=1970, tsstep=15)
        wdmtoolbox.csvtowdm(
            self.wdmname,
            101,
            input_ts=os.path.join(self.test_dir, "nwisiv_02246000.csv"),
        )
        with self.assertRaisesRegex(WDMError, "error code -81"):
            ret1 = wdmtoolbox.extract(self.wdmname, 32000)

    def test_start_date(self):
        wdmtoolbox.createnewwdm(self.wdmname, overwrite=True)
        wdmtoolbox.createnewdsn(self.wdmname, 101, tcode=2, base_year=1970, tsstep=15)
        wdmtoolbox.csvtowdm(
            self.wdmname,
            101,
            input_ts=os.path.join(self.test_dir, "nwisiv_02246000.csv"),
        )
        ret1 = wdmtoolbox.extract(self.wdmname, 101, start_date="2014-02-21 16:00:00")

        ret3 = tstoolbox.read(
            os.path.join(self.test_dir, "nwisiv_02246000.csv"),
            start_date="2014-02-21 16:00:00",
        )
        ret3.index = ret3.index.tz_localize(None)
        ret3 = tsutils.asbestfreq(ret3)
        ret1.columns = ["02246000_iv_00060"]
        assert_frame_equal(ret1, ret3, check_index_type=False)

    def test_end_date(self):
        wdmtoolbox.createnewwdm(self.wdmname, overwrite=True)
        wdmtoolbox.createnewdsn(self.wdmname, 101, tcode=2, base_year=1970, tsstep=15)
        wdmtoolbox.csvtowdm(
            self.wdmname,
            101,
            input_ts=os.path.join(self.test_dir, "nwisiv_02246000.csv"),
        )
        ret1 = wdmtoolbox.extract(self.wdmname, 101, end_date="2014-02-22 11:00:00")

        ret3 = tstoolbox.read(
            os.path.join(self.test_dir, "nwisiv_02246000.csv"),
            end_date="2014-02-22 11:00:00",
        )
        ret3.index = ret3.index.tz_localize(None)
        ret3 = tsutils.asbestfreq(ret3)
        ret1.columns = ["02246000_iv_00060"]
        assert_frame_equal(ret1, ret3, check_index_type=False)

    def test_dates(self):
        wdmtoolbox.createnewwdm(self.wdmname, overwrite=True)
        wdmtoolbox.createnewdsn(self.wdmname, 101, tcode=2, base_year=1970, tsstep=15)
        wdmtoolbox.csvtowdm(
            self.wdmname,
            101,
            input_ts=os.path.join(self.test_dir, "nwisiv_02246000.csv"),
        )
        ret1 = wdmtoolbox.extract(
            self.wdmname,
            101,
            start_date="2014-02-21 16:00:00",
            end_date="2014-02-22 11:00:00",
        )

        ret3 = tstoolbox.read(
            os.path.join(self.test_dir, "nwisiv_02246000.csv"),
            start_date="2014-02-21 16:00:00",
            end_date="2014-02-22 11:00:00",
        )
        ret3.index = ret3.index.tz_localize(None)
        ret3 = tsutils.asbestfreq(ret3)
        ret1.columns = ["02246000_iv_00060"]
        assert_frame_equal(ret1, ret3, check_index_type=False)
