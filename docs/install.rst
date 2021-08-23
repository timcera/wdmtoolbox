Installation for Mere Mortals
=============================

Pre-compiled
++++++++++++

Windows
-------
I used the Appveyor service to compile "wdmtoolbox" on Windows for Python 3.7,
3.8, and 3.9.  These versions are available via `pip`.

On Windows, the best solution for Python is `conda`, however there is some
conflict between `conda install ...` and `pip install ...` that should be
noted.  What works best is to install everything that is available with `conda
install ...` first.

1. Download and install either "conda" or "miniconda" in 32 or 64 bit versions
   according to your machine. https://conda.io/docs/get-started.html
2. Open "Anaconda Prompt".
3. Create a Python 3.7, 3.8, or 3.9 environment and activate it.  For the
   example below I am going to create a Python 3.9 environment called py39.::

       conda env -n py39 python=3.9
       activate py39

4. Install everything that you can using "conda".  I made the following lines
   short so they would be less likely to wrap, but you can install in any
   order.::

       conda install pandas scipy matplotlib
       conda install sphinx ruamel.yaml regex
       conda install lockfile tabulate tzlocal

5. Install "wdmtoolbox" using "pip".::

       pip install wdmtoolbox

6. Use "wdmtoolbox"!::

       wdmtoolbox --help

A convenient way to use "wdmtoolbox" is to put the command that you would type
at the command prompt into a batch file.  A batch file is a text file (editable
by any text editor) with a ".bat" file name extension.  Then you can run all of
the commands in the batch file by running the batch file.

Next time you open the "Anaconda Prompt" to use "wdmtoolbox" you have to
activate the environment where it is installed.

Compile From Source
+++++++++++++++++++

Windows
-------
I use http://appveyor.com to compile the 32-bit version and Github Actions to
compile the 64-bit versions.  Getting the "appveyor.yml" and Github workflow
configuration files right is a nightmare, but finally figured it out.

You should be able to compile it in other ways if you know your way around
Windows, Python, and FORTRAN development.  The minimal environment that
is needed is to have the same "C" compiler as was used to compile your target
Python version (for Python 3.x it is the "C" compiler with Microsoft Visual
Studio 2019), and a FORTRAN compiler (for example Mingw compilers that come
with MSYS2).

Linux
-----
Why I don't use "conda" on Linux:

* I really didn't like how "conda" was overriding system
  libraries on Linux.  Really?
* Is "gdal" fixed yet?
* The wild, wild west of anaconda.org

I went back to virtual environments using "pip" to install everything.  Works
very well since the big players (numpy, scipy, pandas, and matplotlib) now
deliver wheels.

1. Need to have "gcc" and "gfortran" installed.
2. Make whatever 3.7, 3.8, or 3.9 Python environment you want and activate it.
3. I have had to install the "wheel" library first and then the basic science
   stack individually::

       pip install wheel
       pip install numpy
       pip install pandas
       pip install matplotlib
       pip install sphinx

4. Install "wdmtoolbox"::

       pip install wdmtoolbox
