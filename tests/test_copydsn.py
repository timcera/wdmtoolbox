# -*- coding: utf-8 -*-

"""
test_copydsn
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
        self.afd, self.awdmname = tempfile.mkstemp(suffix=".wdm")
        os.close(self.afd)
        self.test_dir = os.path.abspath(os.path.dirname(__file__))

    def tearDown(self):
        os.remove(self.wdmname)
        os.remove(self.awdmname)

    def test_copy_to_self(self):
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

        wdmtoolbox.copydsn(self.wdmname, 101, self.wdmname, 1101)

    def test_listdsns(self):
        wdmtoolbox.createnewwdm(self.wdmname, overwrite=True)
        wdmtoolbox.createnewdsn(self.wdmname, 101, tcode=2, base_year=1970, tsstep=15)
        wdmtoolbox.csvtowdm(
            self.wdmname,
            101,
            input_ts=os.path.join(self.test_dir, "nwisiv_02246000.csv"),
        )
        wdmtoolbox.createnewwdm(self.awdmname, overwrite=True)
        wdmtoolbox.copydsn(self.wdmname, 101, self.awdmname, 1101)
