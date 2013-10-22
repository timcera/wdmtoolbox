
from numpy.distutils.core import Extension, setup
import os
import sys

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()

version = open("VERSION").readline().strip()

install_requires = [
    # List your project dependencies here.
    # For more details, see:
    # http://packages.python.org/distribute/setuptools.html#declaring-dependencies
    'baker >= 1.3',
    'python-dateutil >= 2.1',
    'pandas >= 0.9.0',
    'tstoolbox >= 0.5',
]


setup(name='wdmtoolbox',
      ext_modules=[Extension('wdm', [
          'wdm_support/wdm.pyf',
          'wdm_support/DTTM90.f',
          'wdm_support/TSBUFR.f',
          'wdm_support/UTCHAR.f',
          'wdm_support/UTCP90.f',
          'wdm_support/UTDATE.f',
          'wdm_support/UTNUMB.f',
          'wdm_support/UTWDMD.f',
          'wdm_support/UTWDMF.f',
          'wdm_support/UTWDT1.f',
          'wdm_support/WDATM1.f',
          'wdm_support/WDATM2.f',
          'wdm_support/WDATRB.f',
          'wdm_support/WDBTCH.f',
          'wdm_support/WDMESS.f',
          'wdm_support/WDMID.f',
          'wdm_support/WDOP.f',
          'wdm_support/WDTMS1.f',
          'wdm_support/WDTMS2.f',
          ],
          include_dirs=['wdm_support'])],

      version=version,
      description="Read and write Watershed Data Management (WDM) files",
      long_description=README,
      classifiers=[
          # Get strings from
          # http://pypi.python.org/pypi?%3Aaction=list_classifiers
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Science/Research',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: Developers',
          'Environment :: Console',
          'License :: OSI Approved :: BSD License',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3',
          'Topic :: Scientific/Engineering',
          'Topic :: Software Development :: Libraries :: Python Modules',
          ],
      keywords='WDM watershed data_management data hydrology hydrological simulation fortran HSPF',
      author='Tim Cera, P.E.',
      author_email='tim@cerazone.net',
      url='http://pypi.python.org/pypi/wdmtoolbox',
      license='GPL2',
      packages=['wdmtoolbox'],
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      data_files=[(os.path.join(sys.prefix, 'share', 'wdmtoolbox'),
          ['data/message.wdm'])],
      entry_points={
          'console_scripts':
          ['wdmtoolbox=wdmtoolbox:main']
          }
      )
