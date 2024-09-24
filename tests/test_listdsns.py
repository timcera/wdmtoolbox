"""
test_listdsns
----------------------------------

Tests for `wdmtoolbox` module.
"""

import sys

try:
    from cStringIO import StringIO
except Exception:
    from io import StringIO


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


def test_listdsns_verify(request):
    datadir = request.config.rootdir / "tests"
    wdmtoolbox.listdsns(str(datadir / "MA190049.wdm"))
