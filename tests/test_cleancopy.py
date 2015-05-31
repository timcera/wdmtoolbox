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
        self.tfd, self.twdmname = tempfile.mkstemp(suffix='.wdm')

    def tearDown(self):
        os.close(self.fd)
        os.remove(self.wdmname)
        os.close(self.tfd)
        os.remove(self.twdmname)

    def test_cleancopytoself(self):
        wdmtoolbox.createnewwdm(self.wdmname, overwrite=True)
        wdmtoolbox.createnewdsn(self.wdmname, 101, tcode=2,
                                      base_year=1970, tsstep=15)
        wdmtoolbox.csvtowdm(self.wdmname, 101,
                            input_ts='tests/nwisiv_02246000.csv')
        with assertRaisesRegexp(ValueError,
                'The "inwdmpath" cannot be the same as "outwdmpath"'):
            wdmtoolbox.cleancopywdm(self.wdmname, self.wdmname)

    def test_cleancopy_a_to_b(self):
        wdmtoolbox.createnewwdm(self.wdmname, overwrite=True)
        wdmtoolbox.createnewdsn(self.wdmname, 101, tcode=2,
                                      base_year=1970, tsstep=15)
        wdmtoolbox.csvtowdm(self.wdmname, 101,
                            input_ts='tests/nwisiv_02246000.csv')
        wdmtoolbox.cleancopywdm(self.wdmname, self.twdmname, overwrite=True)

