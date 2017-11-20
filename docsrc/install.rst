Installation for Mere Mortals
=============================

Windows
-------

Pre-compiled
++++++++++++
My "wdmtoolbox" on Windows I have only been able to compile for Python 2.7 and
Python 3.4 so you have to create one of those environments.  

On Windows, I think the best solution is "conda".

1. Download and install either "conda" or "miniconda" in 32 or 64 bit versions
   according to your machine. https://conda.io/docs/get-started.html
2. Open "Anaconda Prompt".
3. Create a Python 2.7 or Python 3.4 environment and activate it.  For the
   example below I am going to create a Python 3.4 environment called py34.::

       conda env -n py34 python=3.4
       activate py34

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
I use "mingwpy" and http://appveyor.com to compile "wdmtoolbox" for Windows.
That is why I am limited to Python 2.7 and 3.4 since those are the only
versions offered by "mingwpy".

You should be able to compile it in other ways.  The minimal environment that
is needed is to have the same "C" compiler as was used to compile your target
Python version, and a FORTRAN compiler.

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
2. Make whatever 2.7+/3.+ Python environment you want and activate it.
3. I have had to install the "wheel" library first and then the basic science
   stack individually::

       pip install wheel
       pip install numpy
       pip install pandas
       pip install matplotlib
       pip install sphinx

4. Install "wdmtoolbox"::

       pip install wdmtoolbox

