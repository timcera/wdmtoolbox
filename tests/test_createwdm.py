

import subprocess
import os
import time

def _createwdm(fname):
    return subprocess.call(['wdmtoolbox',
                            'createnewwdm',
                            '--overwrite',
                            fname])

def test_createwdm():
    fname = os.path.join(os.path.dirname(__file__), 'a.wdm')
    assert _createwdm(fname) == 0
    # A brand spanking new wdm should be 40k
    assert os.path.getsize(fname) == 40*1024
    os.remove(fname)

def test_createnewdsn_checkdefaults():
    fname = os.path.join(os.path.dirname(__file__), 'b.wdm')
    assert _createwdm(fname) == 0
    retcode = subprocess.call(['wdmtoolbox', 'createnewdsn', fname, '101'])
    assert retcode == 0
    tstr = ['#DSN  SCENARIO LOCATION CONSTITUENT START DATE          END DATE            TCODE TSTEP\n',
            '  101                               None                None                    D(4) 1\n']
    p = subprocess.Popen(['wdmtoolbox', 'listdsns', fname],
        stdout=subprocess.PIPE,
        universal_newlines=True)

    # a fake 'p.wait' that won't deadlock?
    # Needed to ensure that 'p.returncode' is available
    while p.poll() == None:
        time.sleep(0.1)
    assert p.returncode == 0

    assert p.stdout.readlines() == tstr
    os.remove(fname)
