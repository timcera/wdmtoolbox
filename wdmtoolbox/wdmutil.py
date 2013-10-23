#!/usr/bin/env python2

from __future__ import print_function

'''
The WDM class supplies a series of utilities for working with WDM files
with Python.  The class uses f2py to wrap the minimally necessary WDM
routines.
'''

import datetime
import os
import os.path
import re
import sys

import pandas as pd

import wdm

# Load in WDM subroutines

# Mapping between WDM TCODE and pandas interval code
MAPTCODE = {
    1: 'S',
    2: 'T',
    3: 'H',
    4: 'D',
    5: 'M',
    6: 'A',
    }

MAPFREQ = {
    'S': 1,
    'T': 2,
    'H': 3,
    'D': 4,
    'M': 5,
    'A': 6,
    }


class WDMError(Exception):
    pass


class DSNDoesNotExist(Exception):
    pass


class LibraryNotFoundError(Exception):
    pass


class WDMFileExists(Exception):
    def __init__(self, filename):
        self.filename = filename

    def __str__(self):
        return 'File {0} exists.'.format(self.filename)


class DSNExistsError(Exception):
    def __init__(self, dsn):
        self.dsn = dsn

    def __str__(self):
        return 'DSN {0} exists.'.format(self.dsn)


class WDM():
    ''' Class to open and read from WDM files.
    '''
    def __init__(self):

        # timcvt: Convert times to account for 24 hour
        # timdif: Time difference
        # wdmopn: Open WDM file
        # wdbsac: Set string attribute
        # wdbsai: Set integer attribute
        # wdbsar: Set real attribute
        # wdbckt: Check if DSN exists
        # wdflcl: Close WDM file
        # wdlbax: Create label for new DSN
        # wdtget: Get time-series data
        # wdtput: Write time-series data
        # wddsrn: Renumber a DSN
        # wddsdl: Delete a DSN
        # wddscl: Copy a label

        self.timcvt = wdm.timcvt
        self.timdif = wdm.timdif
        self.wdbopn = wdm.wdbopn
        self.wdbsac = wdm.wdbsac
        self.wdbsai = wdm.wdbsai
        self.wdbsar = wdm.wdbsar
        self.wdbsgc = wdm.wdbsgc
        self.wdbsgi = wdm.wdbsgi
        self.wdbsgr = wdm.wdbsgr
        self.wdckdt = wdm.wdckdt
        self.wdflcl = wdm.wdflcl
        self.wdlbax = wdm.wdlbax
        self.wdtget = wdm.wdtget
        self.wdtput = wdm.wdtput
        self.wtfndt = wdm.wtfndt
        self.wddsrn = wdm.wddsrn
        self.wddsdl = wdm.wddsdl
        self.wddscl = wdm.wddscl

        self.openfiles = {}

    def wmsgop(self):
        # WMSGOP is a simple open of the message file

        afilename = os.path.join(sys.prefix,
                                 'share',
                                 'wdmtoolbox',
                                 'message.wdm')
        afilename = os.path.relpath(afilename)
        return self._open(afilename, 100, ronwfg=1)

    def dateconverter(self, datestr):
        words = re.findall(r'\d+', str(datestr))
        words = [int(i) for i in words]
        dtime = [1900, 1, 1, 0, 0, 0]
        dtime[:len(words)] = words
        return dtime

    def _open(self, wdname, wdmsfl, ronwfg=0):
        ''' Private method to open WDM file.
        '''
        if wdname not in self.openfiles:
            wdname = wdname.strip()
            assert len(wdname) <= 64
            if ronwfg == 1:
                if not os.path.exists(wdname):
                    raise ValueError('''

    Trying to open
    {0}
    in read-only mode and it cannot be found.

    '''.format(wdname))
            retcode = self.wdbopn(wdmsfl,
                                  wdname,
                                  ronwfg)
            self._retcode_check(retcode, additional_info='wdbopn')
            self.openfiles[wdname] = wdmsfl
        return wdmsfl

    def _retcode_check(self, retcode, additional_info=' '):
        if retcode < 0:
            raise WDMError('''

    WDM library function returned error code {0}. {1}

'''.format(retcode, additional_info))

    def renumber_dsn(self, wdmpath, odsn, ndsn):
        odsn = int(odsn)
        ndsn = int(ndsn)

        wdmfp = self._open(wdmpath, 101)
        retcode = self.wddsrn(
            wdmfp,
            odsn,
            ndsn)
        self._close(wdmpath)
        self._retcode_check(retcode, additional_info='wddsrn')

    def delete_dsn(self, wdmpath, dsn):
        dsn = int(dsn)

        wdmfp = self._open(wdmpath, 101)
        if self.wdckdt(wdmfp, dsn) != 0:
            retcode = self.wddsdl(
                wdmfp,
                dsn)
            self._retcode_check(retcode, additional_info='wddsdl')
        self._close(wdmpath)

    def copydsnlabel(self, inwdmpath, indsn, outwdmpath, outdsn):
        assert inwdmpath != outwdmpath
        indsn = int(indsn)
        outdsn = int(outdsn)
        dsntype = 0
        inwdmfp = self._open(inwdmpath, 101)
        outwdmfp = self._open(outwdmpath, 102)
        retcode = self.wddscl(
            inwdmfp,
            indsn,
            outwdmfp,
            outdsn,
            dsntype)
        self._close(inwdmpath)
        self._close(outwdmpath)
        self._retcode_check(retcode, additional_info='wddscl')

    def describe_dsn(self, wdmpath, dsn):
        wdmfp = self._open(wdmpath, 101)
        if self.wdckdt(wdmfp, dsn) == 0:
            raise DSNDoesNotExist

        tdsfrc, llsdat, lledat, retcode = self.wtfndt(
            wdmfp,
            dsn,
            1)  # GPFLG  - get(1)/put(2) flag
        # Ignore retcode == -6 which means that the dsn doesn't have any data.
        # It it is a new dsn, of course it doesn't have any data.
        if retcode == -6:
            retcode = 0
        self._retcode_check(retcode, additional_info='wtfndt')

        tstep, retcode = self.wdbsgi(
            wdmfp,
            dsn,
            33,  # saind = 33 for time step
            1)   # salen
        self._retcode_check(retcode, additional_info='wdbsgi')

        tcode, retcode = self.wdbsgi(
            wdmfp,
            dsn,
            17,  # saind = 17 for time code
            1)   # salen
        self._retcode_check(retcode, additional_info='wdbsgi')

        tsfill, retcode = self.wdbsgr(
            wdmfp,
            dsn,
            32,  # saind = 32 for tsfill
            1)   # salen
        # retcode = -107 if attribute not present
        if retcode == -107:
            # Since I use tsfill if not found will set to default.
            tsfill = -999.0
            retcode = 0
        else:
            tsfill = tsfill[0]
        self._retcode_check(retcode, additional_info='wdbsgr')

        ostr, retcode = self.wdbsgc(
            wdmfp,
            dsn,
            290,    # saind = 290 for location
            8)      # salen
        self._retcode_check(retcode, additional_info='wdbsgr')

        scen_ostr, retcode = self.wdbsgc(
            wdmfp,
            dsn,
            288,    # saind = 288 for scenario
            8)      # salen
        self._retcode_check(retcode, additional_info='wdbsgr')

        con_ostr, retcode = self.wdbsgc(
            wdmfp,
            dsn,
            289,    # saind = 289 for constitiuent
            8)      # salen
        self._retcode_check(retcode, additional_info='wdbsgr')

        self._close(wdmpath)

        self.timcvt(llsdat)
        self.timcvt(lledat)
        try:
            sdate = datetime.datetime(*llsdat).isoformat()
        except ValueError:
            sdate = None
        try:
            edate = datetime.datetime(*lledat).isoformat()
        except ValueError:
            edate = None

        tstep = tstep[0]
        tcode = tcode[0]
        ostr = ''.join(ostr.tolist())
        scen_ostr = ''.join(scen_ostr.tolist())
        con_ostr = ''.join(con_ostr.tolist())

        return {'dsn':         dsn,
                'start_date':  sdate,
                'end_date':    edate,
                'llsdat':      llsdat,
                'lledat':      lledat,
                'tstep':       tstep,
                'tcode':       tcode,
                'tcode_name':  MAPTCODE[tcode],
                'location':    ostr.strip(),
                'scenario':    scen_ostr.strip(),
                'constituent': con_ostr.strip(),
                'tsfill':      tsfill}

    def create_new_wdm(self, wdmpath, overwrite=False):
        ''' Create a new WDM fileronwfg
        '''
        if overwrite and os.path.exists(wdmpath):
            os.remove(wdmpath)
        elif os.path.exists(wdmpath):
            raise WDMFileExists(wdmpath)
        ronwfg = 2
        wdmfp = self._open(wdmpath, 101, ronwfg=ronwfg)
        self._close(wdmpath)

    def create_new_dsn(self, wdmpath, dsn, tstype='', base_year=1900, tcode=4,
                       tsstep=1, statid=' ', scenario='', location='',
                       description='', constituent='', tsfill=-999.0):
        ''' Create self.wdmfp/dsn. '''
        wdmfp = self._open(wdmpath, 101)
        messfp = self.wmsgop()

        if self.wdckdt(wdmfp, dsn) == 1:
            raise DSNExistsError(dsn)

        # Parameters for wdlbax taken from ATCTSfile/clsTSerWDM.cls
        psa = self.wdlbax(
            wdmfp,
            dsn,
            1,    # DSTYPE - always 1 for time series
            10,   # NDN    - number of down pointers
            10,   # NUP    - number of up pointers
            30,   # NSA    - number of search attributes
            100,  # NSASP  - amount of search attribute space
            300)  # NDP    - number of data pointers
                  # PSA    - pointer to search attribute space

        for saind, salen, saval in [(34, 1, 6),  # tgroup
                                    (83, 1, 1),  # compfg
                                    (84, 1, 1),  # tsform
                                    (85, 1, 1),  # vbtime
                                    (17, 1, int(tcode)),  # tcode
                                    (33, 1, int(tsstep)),  # tsstep
                                    (27, 1, int(base_year)),  # tsbyr
                                    ]:
            retcode = self.wdbsai(
                wdmfp,
                dsn,
                messfp,
                saind,
                salen,
                saval)
            self._retcode_check(retcode, additional_info='wdbsai')

        for saind, salen, saval in [(32, 1, tsfill)]:  # tsfill
            retcode = self.wdbsar(
                wdmfp,
                dsn,
                messfp,
                saind,
                salen,
                saval)
            self._retcode_check(retcode, additional_info='wdbsar')

        for saind, salen, saval, error_name in [
            (2, 16, statid, 'Station ID'),
            (1, 4, tstype.upper(), 'Time series type - tstype'),
            (45, 48, description.upper(), 'Description'),
            (288, 8, scenario.upper(), 'Scenario'),
            (289, 8, constituent.upper(), 'Constituent'),
            (290, 8, location.upper(), 'Location'),
                ]:
            saval = saval.strip()
            if len(saval) > salen:
                raise ValueError('''

    String "{0}" is too long for {1}.  Must
    have a length equal or less than {2}.

'''.format(saval, error_name, salen))

            saval = '{0: <{1}}'.format(saval, salen)

            retcode = self.wdbsac(
                wdmfp,
                dsn,
                messfp,
                saind,
                salen,
                saval)
            self._retcode_check(retcode, additional_info='wdbsac')
        self._close(wdmpath)

    def _tcode_date(self, tcode, date):
        ''' Uses tcode to set the significant parts of the date tuple. '''
        rdate = [1, 1, 1, 0, 0, 0]
        if tcode <= 6:
            rdate[0] = date[0]
        if tcode <= 5:
            rdate[1] = date[1]
        if tcode <= 4:
            rdate[2] = date[2]
        if tcode <= 3:
            rdate[3] = date[3]
        if tcode <= 2:
            rdate[4] = date[4]
        if tcode <= 1:
            rdate[5] = date[5]
        return rdate

    def write_dsn(self, wdmpath, dsn, data, start_date):
        ''' Write to self.wdmfp/dsn the time-series data. '''
        dsn_desc = self.describe_dsn(wdmpath, dsn)
        tcode = dsn_desc['tcode']
        tstep = dsn_desc['tstep']

        dstart_date = start_date.timetuple()[:6]
        llsdat = self._tcode_date(tcode, dstart_date)

        nval = len(data)

        wdmfp = self._open(wdmpath, 101)
        retcode = self.wdtput(
            wdmfp,
            dsn,
            tstep,
            llsdat,
            nval,
            1,
            0,
            tcode,
            data)
        self._close(wdmpath)
        self._retcode_check(retcode, additional_info='wdtput')

    def read_dsn(self, wdmpath, dsn, start_date=None, end_date=None):
        ''' Read from a DSN.
        '''

        # Call wdatim_ to get LLSDAT, LLEDAT, TSTEP, TCODE
        desc_dsn = self.describe_dsn(wdmpath, dsn)

        llsdat = desc_dsn['llsdat']
        lledat = desc_dsn['lledat']
        tcode = desc_dsn['tcode']
        tstep = desc_dsn['tstep']

        # These calls convert 24 to midnight of the next day
        self.timcvt(llsdat)
        self.timcvt(lledat)

        if start_date is not None:
            start_date = self.dateconverter(start_date)
            llsdat = start_date
        if end_date is not None:
            end_date = self.dateconverter(end_date)
            lledat = end_date

        # Determine the number of values (ITERM) from LLSDAT to LLEDAT
        iterm = self.timdif(
            llsdat,
            lledat,
            tcode,
            tstep)

        dtran = 0
        qualfg = 30
        # Get the data and put it into dictionary
        wdmfp = self._open(wdmpath, 101)
        dataout, retcode = self.wdtget(
            wdmfp,
            dsn,
            tstep,
            llsdat,
            iterm,
            dtran,
            qualfg,
            tcode)
        self._close(wdmpath)
        self._retcode_check(retcode, additional_info='wdtget')

        # Find the begining in datetime.datetime format
        tstart = datetime.datetime(llsdat[0],
                                   llsdat[1],
                                   llsdat[2],
                                   llsdat[3],
                                   llsdat[4],
                                   llsdat[5])

        # Convert time series to pandas DataFrame
        index = pd.date_range(
            tstart,
            periods=len(dataout),
            freq=MAPTCODE[tcode])

        tmpval = pd.DataFrame(
            pd.Series(
                dataout,
                index=index,
                name='{0}_DSN_{1}'.format(
                    os.path.basename(wdmpath), dsn)))
        return tmpval

    def read_dsn_por(self, wdmpath, dsn):
        ''' Read the period of record for a DSN.
        '''
        return self.read_dsn(wdmpath, dsn, start_date=None, end_date=None)

    def _close(self, wdmpath):
        ''' Close the WDM file.
        '''
        if wdmpath in self.openfiles:
            retcode = self.wdflcl(self.openfiles[wdmpath])
            self._retcode_check(retcode, additional_info='wdflcl')
            toss = self.openfiles.pop(wdmpath)


if __name__ == '__main__':
    wdm_obj = WDM()
    fname = 'test.wdm'
    if os.name == 'nt':
        fname = r'c:\test.wdm'
    wdm_obj.create_new_wdm(fname, overwrite=True)
    listonumbers = [34.2, 35.0, 36.9, 38.2, 40.2, 20.1, 18.4, 23.6]
    wdm_obj.create_new_dsn(fname, 1003, tstype='EXAM', scenario='OBSERVED', tcode=4, location='EXAMPLE')
    wdm_obj.write_dsn(fname, 1003, listonumbers, datetime.datetime(2000, 1, 1))
    print(wdm_obj.read_dsn_por(fname, 1003))