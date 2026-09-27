"""
test_listdsns
----------------------------------

Tests for `wdmtoolbox` module.
"""

# Standard library imports
import sys

try:
    # Third party imports
    from cStringIO import StringIO
except ImportError:
    # Standard library imports
    from io import StringIO


# First party imports
from wdmtoolbox import wdmtoolbox


def capture(func, *args, **kwds):
    sys.stdout = StringIO()  # capture output
    out = func(*args, **kwds)
    out = sys.stdout.getvalue()  # release output
    try:
        out = bytes(out, "utf-8")
    except TypeError:
        pass
    return out


def test_listdsns_verify(request):
    datadir = request.config.rootdir / "tests"
    wdmtoolbox.listdsns(str(datadir / "MA190049.wdm"))
