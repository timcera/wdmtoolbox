project('wdmtoolbox', ['c', 'fortran'],
    version : run_command(
            ['python', '-c', 'print(open("VERSION").readline(), end="")'],
            check: true
        ).stdout().strip(),
    default_options : ['warning_level=3']
    )

py_mod = import('python')
py = py_mod.find_installation(pure: false)
py_dep = py.dependency()

incdir_numpy = run_command(py,
    ['-c', 'import os; os.chdir(".."); import numpy; print(numpy.get_include())'],
    check : true
).stdout().strip()

incdir_f2py = run_command(py,
    ['-c', 'import os; os.chdir(".."); import numpy.f2py; print(numpy.f2py.get_include())'],
    check : true
).stdout().strip()

inc_np = include_directories(incdir_numpy, incdir_f2py)

ftn_sources = [
    'wdm_support/DTTM90.f', 'wdm_support/TSBUFR.f', 'wdm_support/UTCHAR.f',
    'wdm_support/UTCP90.f', 'wdm_support/UTDATE.f', 'wdm_support/UTNUMB.f',
    'wdm_support/UTWDMD.f', 'wdm_support/UTWDMF.f', 'wdm_support/UTWDT1.f',
    'wdm_support/WDATM1.f', 'wdm_support/WDATM2.f', 'wdm_support/WDATRB.f',
    'wdm_support/WDBTCH.f', 'wdm_support/WDMESS.f', 'wdm_support/WDMID.f',
    'wdm_support/WDOP.f', 'wdm_support/WDTMS1.f', 'wdm_support/WDTMS2.f',
    ]

wdm_source = custom_target('_wdm_libmodule.c',
    input : ftn_sources,
    output : ['_wdm_libmodule.c', '_wdm_lib-f2pywrappers.f'],
    command : [py, '-m', 'numpy.f2py',
        '@INPUT@',
        '-m', '_wdm_lib',
        '--lower',
        '--backend', 'meson',
        'only:',
        'timcvt', 'timdif', 'wdbopn', 'wdbsac', 'wdbsai', 'wdbsar', 'wdbsgc',
        'wdbsgi', 'wdbsgr', 'wdckdt', 'wdflcl', 'wdlbax', 'wdtget', 'wdtput',
        'wtfndt', 'wddsrn', 'wddsdl', 'wddscl', 'wdsagy', 'wdbsgx',
    ]
)

py.extension_module('_wdm_lib',
    [
        ftn_sources,
        wdm_source,
        incdir_f2py / 'fortranobject.c'
    ],
    include_directories: inc_np,
    dependencies : py_dep,
    install : true,
    install_dir: py.get_install_dir() / 'wdmtoolbox',
)

subdir('src')
