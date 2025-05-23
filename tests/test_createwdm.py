import os
import shlex
import subprocess
import sys
import tempfile
from unittest import TestCase

from wdmtoolbox import wdmtoolbox
from wdmtoolbox.wdmutil import WDMFileExists

try:
    from cStringIO import StringIO
except Exception:
    from io import StringIO


def _createwdm(fname):
    cmd = shlex.split(f"wdmtoolbox createnewwdm --overwrite {fname}")
    return subprocess.call(cmd)


def test_createwdm():
    fd, fname = tempfile.mkstemp(suffix=".wdm")
    os.close(fd)
    assert _createwdm(fname) == 0
    wdmtoolbox.createnewwdm(fname, overwrite=True)
    # A brand spanking new wdm should be 40k
    assert os.path.getsize(fname) == 40 * 1024
    os.remove(fname)


def test_createnewdsn_checkdefaults():
    fd, fname = tempfile.mkstemp(suffix=".wdm")
    os.close(fd)
    assert _createwdm(fname) == 0
    cmd = shlex.split(f"wdmtoolbox createnewdsn {fname} 101")
    retcode = subprocess.call(cmd)
    assert retcode == 0
    # tstr = [' DSN  SCENARIO LOCATION CONSTITUENT TSTYPE START_DATE          END_DATE            TCODE TSTEP',
    #         '  101                               NaT                NaT                    4 1',
    #         '']
    # tstr = [i.strip().split() for i in tstr]
    # tstr = [' '.join(i) for i in tstr]
    # tstr = '\n'.join(tstr)
    # cmd = shlex.split('wdmtoolbox listdsns {0}'.format(fname))

    # astr = astr.split('\n')
    # astr = [i.strip().split() for i in astr]
    # astr = [' '.join(i) for i in astr]
    # astr = '\n'.join(astr)
    # print(astr)
    # print(tstr)
    # assert astr == tstr

    os.remove(fname)


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

    def tearDown(self):
        os.remove(self.wdmname)

    def test_overwrite(self):
        wdmtoolbox.createnewwdm(self.wdmname, overwrite=True)
        with self.assertRaisesRegex(WDMFileExists, "exists."):
            wdmtoolbox.createnewwdm(self.wdmname)
