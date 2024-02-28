"""
test_listdsns
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


def test_listdsns_verify(request):
    datadir = request.config.rootdir / "tests"
    wdmtoolbox.listdsns(str(datadir / "MA190049.wdm"))
