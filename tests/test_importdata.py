#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_createnewdsn
----------------------------------

Tests for `tstoolbox` module.
"""

import shlex
import subprocess
import sys
import os
import tempfile
try:
    from cStringIO import StringIO
except:
    from io import StringIO

from pandas.util.testing import TestCase
from pandas.util.testing import assert_frame_equal
from pandas.util.testing import assertRaisesRegexp
import pandas as pd

from tstoolbox import tstoolbox
import tstoolbox.tsutils as tsutils
from wdmtoolbox import wdmtoolbox


def capture(func, *args, **kwds):
    sys.stdout = StringIO()      # capture output
    out = func(*args, **kwds)
    out = sys.stdout.getvalue()  # release output
    try:
        out = bytes(out, 'utf-8')
    except:
        pass
    return out


class TestDescribe(TestCase):
    def setUp(self):
        self.fd, self.wdmname = tempfile.mkstemp(suffix='.wdm')

    def tearDown(self):
        os.close(self.fd)
        os.remove(self.wdmname)

    def test_tstep(self):
        wdmtoolbox.createnewwdm(self.wdmname, overwrite=True)
        wdmtoolbox.createnewdsn(self.wdmname, 101, tcode=2,
                                      base_year=1970, tsstep=15)
        wdmtoolbox.csvtowdm(self.wdmname, 101,
                            input_ts='tests/nwisiv_02246000.csv')
        ret1 = wdmtoolbox.extract(self.wdmname, 101)
        ret2 = wdmtoolbox.extract('{0},101'.format(self.wdmname))
        assert_frame_equal(ret1, ret2)

        ret3 = tstoolbox.read('tests/nwisiv_02246000.csv').astype('float64')
        ret1.columns = ['02246000_iv_00060']
        assert_frame_equal(ret1, ret3)

    def test_extract_args(self):
        wdmtoolbox.createnewwdm(self.wdmname, overwrite=True)
        wdmtoolbox.createnewdsn(self.wdmname, 101, tcode=2,
                                      base_year=1970, tsstep=15)
        wdmtoolbox.csvtowdm(self.wdmname, 101,
                            input_ts='tests/nwisiv_02246000.csv')
        with assertRaisesRegexp(ValueError,
                                'The only allowed keywords are'):
            ret1 = wdmtoolbox.extract(self.wdmname, 101, ph=True)

    def test_listdsns(self):
        wdmtoolbox.createnewwdm(self.wdmname, overwrite=True)
        wdmtoolbox.createnewdsn(self.wdmname, 101, tcode=2,
                                      base_year=1970, tsstep=15)
        wdmtoolbox.csvtowdm(self.wdmname, 101,
                            input_ts='tests/nwisiv_02246000.csv')
        ldsns = wdmtoolbox.listdsns(self.wdmname)

