import shlex
import subprocess
import sys

import numpy as np
from numpy.distutils.core import setup
from numpy.distutils.extension import Extension

pkg_name = "wdmtoolbox"

version = open("VERSION", encoding="ascii").readline().strip()

if sys.argv[-1] == "publish":
    subprocess.run(shlex.split("cleanpy ."), check=True)
    subprocess.run(shlex.split("python setup.py sdist"), check=True)
    subprocess.run(
        shlex.split(f"twine upload --skip-existing dist/{pkg_name}-{version}.tar.gz"),
        check=True,
    )
    subprocess.run(
        shlex.split(f"twine upload --skip-existing dist/{pkg_name}-{version}*.whl"),
        check=True,
    )
    sys.exit()

wdm_support = Extension(
    "_wdm_lib",
    [
        "wdm_support/wdm.pyf",
        "wdm_support/DTTM90.f",
        "wdm_support/TSBUFR.f",
        "wdm_support/UTCHAR.f",
        "wdm_support/UTCP90.f",
        "wdm_support/UTDATE.f",
        "wdm_support/UTNUMB.f",
        "wdm_support/UTWDMD.f",
        "wdm_support/UTWDMF.f",
        "wdm_support/UTWDT1.f",
        "wdm_support/WDATM1.f",
        "wdm_support/WDATM2.f",
        "wdm_support/WDATRB.f",
        "wdm_support/WDBTCH.f",
        "wdm_support/WDMESS.f",
        "wdm_support/WDMID.f",
        "wdm_support/WDOP.f",
        "wdm_support/WDTMS1.f",
        "wdm_support/WDTMS2.f",
    ],
    include_dirs=["wdm_support", np.get_include()],
)

setup(
    ext_modules=[wdm_support],
)
