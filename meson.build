project('wdmtoolbox', 'c',
    version : run_command('python', '-c',
    'print(open("@0@").readline(), end="")'.format('VERSION')
).stdout().strip(),
    default_options : ['warning_level=3'])

add_languages('fortran')

py_mod = import('python')
py = py_mod.find_installation()
py_dep = py.dependency()

incdir_numpy = meson.get_external_property('numpy-include-dir', 'not-given')
if incdir_numpy == 'not-given'
    incdir_numpy = run_command(py,
        [
            '-c',
'''
import os
import numpy as np
try:
    incdir = os.path.abspath(np.get_include())
except Exception:
    incdir = np.get_include()
print(incdir)
'''
        ],
        check: true
    ).stdout().strip()
endif

incdir_f2py = incdir_numpy / '..' / '..' / 'f2py' / 'src'
inc_f2py = include_directories(incdir_f2py)
fortranobject_c = incdir_f2py / 'fortranobject.c'

ftn_sources = ['wdm_support/DTTM90.f', 'wdm_support/TSBUFR.f',
    'wdm_support/UTCHAR.f', 'wdm_support/UTCP90.f', 'wdm_support/UTDATE.f',
    'wdm_support/UTNUMB.f', 'wdm_support/UTWDMD.f', 'wdm_support/UTWDMF.f',
    'wdm_support/UTWDT1.f', 'wdm_support/WDATM1.f', 'wdm_support/WDATM2.f',
    'wdm_support/WDATRB.f', 'wdm_support/WDBTCH.f', 'wdm_support/WDMESS.f',
    'wdm_support/WDMID.f', 'wdm_support/WDOP.f', 'wdm_support/WDTMS1.f',
    'wdm_support/WDTMS2.f']

wdm_source = custom_target('_wdm_libmodule.c',
    input : ftn_sources,
    output : ['_wdm_libmodule.c', '_wdm_lib-f2pywrappers.f'],
    command : [py, '-m', 'numpy.f2py', '@INPUT@', '-m', '_wdm_lib', '--lower',
        'only:',
        'timcvt', 'timdif', 'wdbopn', 'wdbsac', 'wdbsai', 'wdbsar', 'wdbsgc',
        'wdbsgi', 'wdbsgr', 'wdckdt', 'wdflcl', 'wdlbax', 'wdtget', 'wdtput',
        'wtfndt', 'wddsrn', 'wddsdl', 'wddscl', 'wdsagy', 'wdbsgx',
    ]
)

inc_np = include_directories(incdir_numpy, incdir_f2py)
np_dep = declare_dependency(include_directories: inc_np)

py.extension_module('_wdm_lib',
    ftn_sources,
    wdm_source,
    fortranobject_c,
    include_directories: inc_np,
    dependencies : np_dep,
    install : true
)

subdir('src')
