# -*- coding: utf-8 -*-
"""Package __init__.py.

Taken from numpy that they use to import openblas.

Helper to preload windows DLLs to prevent DLL not found errors.
Once a DLL is preloaded, its namespace is made available to any
subsequent DLL.
"""

import glob
import os
import sys
import sysconfig

if os.name == "nt":
    from ctypes import WinDLL

    basedir = sysconfig.get_path("purelib")
    libs_dir = [os.path.abspath(os.path.join(basedir, "_wdm_lib", ".libs"))]
    libs_dir = libs_dir + [
        os.path.abspath(os.path.join(basedir, "wdmtoolbox", ".libs"))
    ]
    for lib in libs_dir:
        for filename in glob.glob(os.path.join(lib, "*.dll")):
            if os.path.exists(filename):
                _ = WinDLL(os.path.abspath(filename))
