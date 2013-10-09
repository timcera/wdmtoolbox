from setuptools import setup
import os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()

version = open("VERSION").readline().strip()

install_requires = [
    # List your project dependencies here.
    # For more details, see:
    # http://packages.python.org/distribute/setuptools.html#declaring-dependencies
    'baker >= 1.3',
    'python-dateutil >= 1.5',    # python-dateutil-2.0 is for Python 3.0
    'pandas >= 0.9.0',
    'tstoolbox >= 0.5',
]


setup(name='wdmtoolbox',
      version=version,
      description="Read and write Watershed Data Management (WDM) files",
      long_description=README,
      classifiers=[
          # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
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
      entry_points={
          'console_scripts':
              ['wdmtoolbox=wdmtoolbox:main']
      }
      )
