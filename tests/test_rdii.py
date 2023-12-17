"""
test_rdii.py
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

from wdmtoolbox import wdmtoolbox


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

    def test_rdii(self):
        wdmtoolbox.createnewwdm(self.wdmname, overwrite=True)
        wdmtoolbox.createnewdsn(self.wdmname, 101, tcode=2, base_year=1970, tsstep=15)
        wdmtoolbox.csvtowdm(
            self.wdmname,
            101,
            input_ts=os.path.join(self.test_dir, "nwisiv_02246000.csv"),
        )
        wdmtoolbox.copydsn(self.wdmname, 101, self.wdmname, 1101)
        wdmtoolbox.wdmtoswmm5rdii(self.wdmname, 101, 1101)
