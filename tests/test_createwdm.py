#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import os
import time
import shlex
import tempfile

def _createwdm(fname):
    cmd = shlex.split('wdmtoolbox createnewwdm --overwrite {0}'.format(fname))
    print(cmd)
    return subprocess.call(cmd)

def test_createwdm():
    fd, fname = tempfile.mkstemp(suffix='.wdm')
    print(fname)
    assert _createwdm(fname) == 0
    # A brand spanking new wdm should be 40k
    assert os.path.getsize(fname) == 40*1024
    os.close(fd)
    os.remove(fname)

def test_createnewdsn_checkdefaults():
    fd, fname = tempfile.mkstemp(suffix='.wdm')
    assert _createwdm(fname) == 0
    retcode = subprocess.call(['wdmtoolbox', 'createnewdsn', fname, '101'])
    assert retcode == 0
    tstr = ['#DSN  SCENARIO LOCATION CONSTITUENT START DATE          END DATE            TCODE TSTEP\n',
            '  101                               None                None                    D(4) 1\n']
    p = subprocess.Popen(['wdmtoolbox', 'listdsns', fname],
        stdout=subprocess.PIPE,
        universal_newlines=True)

    # a fake 'p.wait' that won't deadlock?
    # Needed to ensure that 'p.returncode' is available
    while p.poll() == None:
        time.sleep(0.1)
    assert p.returncode == 0

    assert p.stdout.readlines() == tstr
    os.close(fd)
    os.remove(fname)


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
from wdmtoolbox.wdmutil import WDMError
from wdmtoolbox.wdmutil import DSNDoesNotExist
from wdmtoolbox.wdmutil import WDMFileExists


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

    def test_overwrite(self):
        wdmtoolbox.createnewwdm(self.wdmname, overwrite=True)
        with assertRaisesRegexp(WDMFileExists,
                'exists.'):
            wdmtoolbox.createnewwdm(self.wdmname)

