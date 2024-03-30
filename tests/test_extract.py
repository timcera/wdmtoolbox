"""
test_createnewdsn
----------------------------------

Tests for `wdmtoolbox` module.
"""

import os
import sys
import tempfile

try:
    from cStringIO import StringIO
except Exception:
    from io import StringIO

from unittest import TestCase

from pandas.testing import assert_frame_equal
from toolbox_utils import tsutils

from wdmtoolbox import wdmtoolbox
from wdmtoolbox.wdmutil import WDMError


def capture(func, *args, **kwds):
    sys.stdout = StringIO()  # capture output
    out = func(*args, **kwds)
    out = sys.stdout.getvalue()  # release output
    try:
        out = bytes(out, "utf-8")
    except Exception:
        pass
    return out


class TestDescribe(TestCase):
    def setUp(self):
        self.fd, self.wdmname = tempfile.mkstemp(suffix=".wdm")
        os.close(self.fd)
        self.test_dir = os.path.abspath(os.path.dirname(__file__))

    def tearDown(self):
        os.remove(self.wdmname)

    def test_extract_args(self):
        wdmtoolbox.createnewwdm(self.wdmname, overwrite=True)
        wdmtoolbox.createnewdsn(self.wdmname, 101, tcode=2, base_year=1970, tsstep=15)
        wdmtoolbox.csvtowdm(
            self.wdmname,
            101,
            input_ts=os.path.join(self.test_dir, "nwisiv_02246000.csv"),
        )
        with self.assertRaisesRegex(ValueError, "The only allowed keywords are"):
            wdmtoolbox.extract(self.wdmname, 101, ph=True)

    def test_extract_range(self):
        wdmtoolbox.createnewwdm(self.wdmname, overwrite=True)
        for dsn in range(101, 111):
            wdmtoolbox.createnewdsn(
                self.wdmname, dsn, tcode=2, base_year=1970, tsstep=15
            )
            wdmtoolbox.csvtowdm(
                self.wdmname,
                dsn,
                input_ts=os.path.join(self.test_dir, "nwisiv_02246000.csv"),
            )
        df = wdmtoolbox.extract(self.wdmname, "101:110")
        assert len(df.columns) == 10
        df = wdmtoolbox.extract(self.wdmname, "101:105")
        assert len(df.columns) == 5
        df = wdmtoolbox.extract(self.wdmname, "101:105+106:110")
        assert len(df.columns) == 10
