# -*- coding: utf-8 -*-
#
import os
import sys

import setuptools
from numpy.distutils.core import Extension, setup

# temporarily redirect config directory to prevent matplotlib importing
# testing that for writeable directory which results in sandbox error in
# certain easy_install versions
os.environ["MPLCONFIGDIR"] = "."

pkg_name = "wdmtoolbox"

version = open("VERSION").readline().strip()

if sys.argv[-1] == "publish":
    os.system("cleanpy .")
    os.system("python setup.py sdist")
    os.system("twine upload dist/{pkg_name}-{version}.tar.gz".format(**locals()))
    os.system("twine upload dist/{pkg_name}-{version}*.whl".format(**locals()))
    sys.exit()

README = open("README.rst").read()

install_requires = [
    # List your project dependencies here.
    # For more details, see:
    # http://packages.python.org/distribute/setuptools.html#declaring-dependencies
    "tstoolbox >= 103.17.1",
    "filelock",
]

extras_require = {
    "dev": [
        "black",
        "cleanpy",
        "twine",
        "pytest",
        "coverage",
        "flake8",
        "pytest-cov",
        "pytest-mpl",
        "pre-commit",
        "black-nbconvert",
        "blacken-docs",
        "velin",
        "isort",
        "pyroma",
        "pyupgrade",
        "commitizen",
    ]
}

libraries = []

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
    include_dirs=["wdm_support"],
    libraries=libraries,
)

setup(
    name=pkg_name,
    version=version,
    description="Read and write Watershed Data Management (WDM) files",
    long_description=README,
    classifiers=[
        # Get strings from
        # http://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
        "Environment :: Console",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="WDM watershed data_management data hydrology hydrological simulation fortran HSPF",
    author="Tim Cera, PE",
    author_email="tim@cerazone.net",
    url="http://timcera.bitbucket.io/{pkg_name}/docs/index.html".format(**locals()),
    license="BSD",
    packages=setuptools.find_packages("src"),
    package_dir={"": "src"},
    package_data={"wdmtoolbox": ["message.wdm"]},
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    extras_require=extras_require,
    ext_modules=[wdm_support],
    entry_points={
        "console_scripts": ["{pkg_name}={pkg_name}.{pkg_name}:main".format(**locals())]
    },
    test_suite="tests",
    python_requires=">=3.7.1",
)
