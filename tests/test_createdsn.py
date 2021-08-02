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
from tstoolbox import tstoolbox

from wdmtoolbox import wdmtoolbox
from wdmtoolbox.wdmutil import DSNExistsError


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

    def test_extract(self):
        wdmtoolbox.createnewwdm(self.wdmname, overwrite=True)
        wdmtoolbox.createnewdsn(self.wdmname, 101, tcode=5, base_year=1870)
        wdmtoolbox.csvtowdm(
            self.wdmname, 101, input_ts=os.path.join(self.test_dir, "sunspot_area.csv")
        )
        ret1 = wdmtoolbox.extract(self.wdmname, 101).astype("f")
        ret2 = wdmtoolbox.extract("{},101".format(self.wdmname)).astype("f")
        assert_frame_equal(ret1, ret2)

        ret3 = tstoolbox.read(os.path.join(self.test_dir, "sunspot_area.csv")).astype(
            "f"
        )
        ret1.columns = ["Area"]
        assert_frame_equal(ret1, ret3)

        ret4 = tstoolbox.read(
            os.path.join(self.test_dir, "sunspot_area_with_missing.csv"), dropna="no"
        ).astype("f")

        wdmtoolbox.createnewdsn(self.wdmname, 500, tcode=5, base_year=1870)
        wdmtoolbox.csvtowdm(
            self.wdmname,
            500,
            input_ts=os.path.join(self.test_dir, "sunspot_area_with_missing.csv"),
        )
        ret5 = wdmtoolbox.extract(self.wdmname, 500).astype("f")
        ret5.columns = ["Area"]
        assert_frame_equal(ret5, ret4)

    def test_dsn_exists(self):
        wdmtoolbox.createnewwdm(self.wdmname, overwrite=True)
        wdmtoolbox.createnewdsn(self.wdmname, 101, tcode=5, base_year=1870)
        with self.assertRaisesRegex(DSNExistsError, "exists."):
            wdmtoolbox.createnewdsn(self.wdmname, 101, tcode=5, base_year=1870)
