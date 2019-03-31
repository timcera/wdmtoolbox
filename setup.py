
import setuptools
from numpy.distutils.core import Extension, setup
import os
import sys

import distutils.command.build_ext    #imports distutils.core, too
d = distutils.core.Distribution()
b = distutils.command.build_ext.build_ext(d)  #or `d.get_command_class('build_ext')(d)',
                                              # then it's enough to import distutils.core
b.finalize_options()

# temporarily redirect config directory to prevent matplotlib importing
# testing that for writeable directory which results in sandbox error in
# certain easy_install versions
os.environ["MPLCONFIGDIR"] = "."

version = open("VERSION").readline().strip()

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    os.system('twine upload dist/wdmtoolbox-{0}*.whl'.format(version))
    sys.exit()

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()

install_requires = [
    # List your project dependencies here.
    # For more details, see:
    # http://packages.python.org/distribute/setuptools.html#declaring-dependencies
    'tstoolbox >= 30.76.35.23',
    'filelock',
]

libraries = []
rld = b.library_dirs,
if sys.platform.startswith('win'):
    libraries = ['quadmath']
    rld = None

wdm_support = Extension('_wdm_lib', [
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
    include_dirs=['wdm_support'],
    libraries=libraries,
    runtime_library_dirs=rld,
)

setup(name='wdmtoolbox',
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
      url='http://timcera.bitbucket.io/wdmtoolbox/docsrc/index.html',
      packages=['wdmtoolbox'],
      package_dir={'wdmtoolbox': 'wdmtoolbox'},
      package_data={'wdmtoolbox': ['message.wdm']},
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      ext_modules=[wdm_support],
      entry_points={
          'console_scripts':
          ['wdmtoolbox=wdmtoolbox.wdmtoolbox:main']
      },
      python_requires='>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*',
      )
