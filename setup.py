import os
import shlex
import shutil
import subprocess
import sys

pkg_name = "wdmtoolbox"

version = open("VERSION", encoding="ascii").readline().strip()

if sys.argv[-1] == "publish":
    subprocess.run(shlex.split("cleanpy ."), check=True)
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("build"):
        shutil.rmtree("build")
    subprocess.run(shlex.split("python -m build"), check=True)
    subprocess.run(
        shlex.split(f"twine upload --skip-existing dist/{pkg_name}-{version}.tar.gz"),
        check=True,
    )
