#!/usr/bin/env python
'''
The WDM class supplies a series of utilities for working with WDM files
with Python.  The class uses ctypes to wrap a specially aggregated library
of WDM subroutines called 'libhass_ent'.  The aggregation of component libraries
'adwdm', 'aide', 'stats', 'util', and 'wdm' is necessary to capture all
possible subroutine calls since ctypes does not allow bringing in more than
one library.
'''

from ctypes import c_int, c_float, c_char, byref, c_char_p, create_string_buffer
from ctypes.util import find_library
import datetime
import os
import os.path
import random
import re

import scikits.timeseries as ts

# Load in WDM subroutines

# Mapping between WDM TCODE and scikits.timeseries interval code
MAPTCODE = {
            1: 'SECOND',
            2: 'MINUTE',
            3: 'HOUR',
            4: 'DAY',
            5: 'MONTH',
            6: 'YEAR',
            }

MAPFREQ = {
           'SECOND': 1,
           'MINUTE': 2,
           'HOUR':   3,
           'DAY':    4,
           'MONTH':  5,
           'YEAR':   6,
           }
# Setup some WDM variables
RETCODE = c_int(1)
TSTEP = c_int(1)
TCODE = c_int(1)
TSFILL = c_float(1)
ITERM = c_int(1)
DTRAN = c_int(0)
QUALFG = c_int(30)
FDATE = c_int * 6
LLSDAT = FDATE()
LLEDAT = FDATE()
AFILE = c_char*64

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
    def __init__(self, libhass_entpath=None):
        ''' Load libhass_ent and initialize WDM environment.
        '''
        # libhass_ent.so -> Linux/Unix library
        # hass_ent.dll -> Windows
        flpath = find_library('hass_ent')

        # Need to try this anyway because find_library does not search
        # LD_LIBRARY_PATH on Linux
        if flpath == None:
            flpath = 'libhass_ent.so'

        if os.name == 'nt':
            from ctypes import windll,cdll
            self.libhass_ent = windll.LoadLibrary(flpath)
        else:
            from ctypes import cdll
            self.libhass_ent = cdll.LoadLibrary(flpath)

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

        # hass_ent.dll has different names than libhass_ent.so on Linux
        if os.name == 'posix':
            wdbfin = self.libhass_ent.f90_wdbfin_
            self.timcvt = self.libhass_ent.f90_timcvt_
            self.timdif = self.libhass_ent.f90_timdif_
            self.wdbopn = self.libhass_ent.f90_wdbopn_
            self.wdbsac = self.libhass_ent.f90_wdbsac_
            self.wdbsai = self.libhass_ent.f90_wdbsai_
            self.wdbsar = self.libhass_ent.f90_wdbsar_
            self.wdbsgc = self.libhass_ent.f90_wdbsgc_xx_
            self.wdbsgi = self.libhass_ent.f90_wdbsgi_
            self.wdbsgr = self.libhass_ent.f90_wdbsgr_
            self.wdckdt = self.libhass_ent.f90_wdckdt_
            self.wdflcl = self.libhass_ent.f90_wdflcl_
            self.wdlbax = self.libhass_ent.f90_wdlbax_
            self.wdtget = self.libhass_ent.f90_wdtget_
            self.wdtput = self.libhass_ent.f90_wdtput_
            self.wtfndt = self.libhass_ent.f90_wtfndt_
            self.wddsrn = self.libhass_ent.f90_wddsrn_
            self.wddsdl = self.libhass_ent.f90_wddsdl_
        if os.name == 'nt':
            wdbfin = self.libhass_ent.F90_WDBFIN
            self.timcvt = self.libhass_ent.F90_TIMCVT
            self.timdif = self.libhass_ent.F90_TIMDIF
            self.wdbopn = self.libhass_ent.F90_WDBOPN
            self.wdbsac = self.libhass_ent.F90_WDBSAC
            self.wdbsai = self.libhass_ent.F90_WDBSAI
            self.wdbsar = self.libhass_ent.F90_WDBSAR
            self.wdbsgc = self.libhass_ent.F90_WDBSGC_XX
            self.wdbsgi = self.libhass_ent.F90_WDBSGI
            self.wdbsgr = self.libhass_ent.F90_WDBSGR
            self.wdckdt = self.libhass_ent.F90_WDCKDT
            self.wdflcl = self.libhass_ent.F90_WDFLCL
            self.wdlbax = self.libhass_ent.F90_WDLBAX
            self.wdtget = self.libhass_ent.F90_WDTGET
            self.wdtput = self.libhass_ent.F90_WDTPUT
            self.wtfndt = self.libhass_ent.F90_WTFNDT
            self.wddsrn = self.libhass_ent.F90_WDDSRN
            self.wddsdl = self.libhass_ent.F90_WDDSDL

        # Initialize WDM environment
        wdbfin()

        self.openfiles = {}

    def wmsgop(self):
        # WMSGOP is a simple open of the message file

        if os.name == 'nt':
            # The following is the default location on Windows.
            afilename = r'C:\Basins\models\HSPF\bin\hspfmsg.wdm'
        elif os.name == 'posix':
            try:
                afilename = os.path.join(os.environ['USGSHOME'], 'share', 'usgs', 'message.wdm')
            except KeyError:
                afilename = os.path.join('usr', 'local', 'share', 'usgs', 'message.wdm')
        return self.__open(afilename, ronwfg=1)

    def dateconverter(self, datestr):
        # This is copied from tsutils.py - don't like that but was having a problem
        # import tsutils tstoolbox - don't know why.
        words = re.findall(r'\d+', str(datestr))
        if len(words) == 1:
            tsdate = ts.Date(freq='yearly',
                             year=int(words[0]))
        if len(words) == 2:
            tsdate = ts.Date(freq='monthly',
                             year=int(words[0]),
                             month=int(words[1]))
        if len(words) == 3:
            tsdate = ts.Date(freq='daily',
                             year=int(words[0]),
                             month=int(words[1]),
                             day=int(words[2]))
        if len(words) == 4:
            tsdate = ts.Date(freq='hourly',
                             year=int(words[0]),
                             month=int(words[1]),
                             day=int(words[2]),
                             hour=int(words[3]))
        if len(words) == 5:
            tsdate = ts.Date(freq='minutely',
                             year=int(words[0]),
                             month=int(words[1]),
                             day=int(words[2]),
                             hour=int(words[3]),
                             minute=int(words[4]))
        if len(words) == 6:
            tsdate = ts.Date(freq='secondly',
                             year=int(words[0]),
                             month=int(words[1]),
                             day=int(words[2]),
                             hour=int(words[3]),
                             minute=int(words[4]),
                             second=int(words[5]))
        return tsdate

    def __open(self, wdmpath, ronwfg=0):
        ''' Private method to open WDM file.
        '''
        if wdmpath not in self.openfiles:
            assert len(wdmpath) <= 64
            nwdmpath = '{0:64}'.format(wdmpath)
            afile = AFILE()
            afile.value = nwdmpath
            wdmfp = self.wdbopn(byref(c_int(ronwfg)),
                        byref(afile),
                        byref(c_int(len(nwdmpath))))
            self.openfiles[wdmpath] = c_int(wdmfp)
        return self.openfiles[wdmpath]

    def __retcode_check(self, retcode, additional_info=' '):
        if retcode.value < 0:
            raise WDMError('WDM library function returned error code {0}. {1}'.format(retcode.value, additional_info))

    def renumber_dsn(self, wdmpath, odsn, ndsn):
        wdmfp = self.__open(wdmpath)
        odsn = c_int(int(odsn))
        ndsn = c_int(int(ndsn))

        self.wddsrn(byref(wdmfp),
                    byref(odsn),
                    byref(ndsn),
                    byref(RETCODE))
        self.__retcode_check(RETCODE, additional_info='wddsrn')

    def delete_dsn(self, wdmpath, dsn):
        wdmfp = self.__open(wdmpath)
        dsn = c_int(int(dsn))

        self.wddsdl(byref(wdmfp),
                    byref(dsn),
                    byref(RETCODE))
        self.__retcode_check(RETCODE, additional_info='wddsdl')

    def describe_dsn(self, wdmpath, dsn):
        wdmfp = self.__open(wdmpath)
        dsn = c_int(int(dsn))
        if self.wdckdt(byref(wdmfp), byref(dsn)) == 0:
            return None
        tdsfrc = c_int(1)
        self.wtfndt(byref(wdmfp),
                    byref(dsn),
                    byref(c_int(1)), # GPFLG  - get(1)/put(2) flag
                    byref(tdsfrc),   # TDSFRC - data-set first record number
                    byref(LLSDAT),   # SDAT   - starting date of data in dsn
                    byref(LLEDAT),   # EDAT   - ending date of data in dsn
                    byref(RETCODE))
        # Ignore RETCODE == -6 which means that the dsn doesn't have any data.
        # It it is a new dsn, of course it doesn't have any data.
        if RETCODE.value == -6:
            RETCODE.value = 0
        self.__retcode_check(RETCODE, additional_info='wtfndt')
        self.timcvt(byref(LLSDAT))
        self.timcvt(byref(LLEDAT))
        try:
            sdate = datetime.datetime(*LLSDAT[:]).isoformat()
        except ValueError:
            sdate = None
        try:
            edate = datetime.datetime(*LLEDAT[:]).isoformat()
        except ValueError:
            edate = None

        self.wdbsgi(byref(wdmfp),
                    byref(dsn),
                    byref(c_int(33)), # saind = 33 for time step
                    byref(c_int(1)),  # salen
                    byref(TSTEP),
                    byref(RETCODE))
        self.__retcode_check(RETCODE, additional_info='wdbsgi')

        self.wdbsgi(byref(wdmfp),
                    byref(dsn),
                    byref(c_int(17)), # saind = 17 for time code
                    byref(c_int(1)),  # salen
                    byref(TCODE),
                    byref(RETCODE))
        self.__retcode_check(RETCODE, additional_info='wdbsgi')

        self.wdbsgr(byref(wdmfp),
                    byref(dsn),
                    byref(c_int(32)), # saind = 32 for tsfill
                    byref(c_int(1)),  # salen
                    byref(TSFILL),
                    byref(RETCODE))
        # RETCODE = -107 if attribute not present
        if RETCODE.value == -107:
            # Since I use TSFILL if not found will set to default.
            TSFILL.value = -999.0
            RETCODE.value = 0
        self.__retcode_check(RETCODE, additional_info='wdbsgr')

        salen = 8
        sints = c_int * salen
        ostr = sints()
        self.wdbsgc(byref(wdmfp),
                    byref(dsn),
                    byref(c_int(290)), # saind = 290 for location
                    byref(c_int(salen)),  # salen
                    byref(ostr))
        ostr = ''.join([chr(i) for i in ostr[:] if i != 0])

        salen = 8
        sints = c_int * salen
        scen_ostr = sints()
        self.wdbsgc(byref(wdmfp),
                    byref(dsn),
                    byref(c_int(288)), # saind = 288 for scenario
                    byref(c_int(salen)),  # salen
                    byref(scen_ostr))
        scen_ostr = ''.join([chr(i) for i in scen_ostr[:] if i != 0])

        salen = 8
        sints = c_int * salen
        con_ostr = sints()
        self.wdbsgc(byref(wdmfp),
                    byref(dsn),
                    byref(c_int(289)), # saind = 289 for constitiuent
                    byref(c_int(salen)),  # salen
                    byref(con_ostr))
        con_ostr = ''.join([chr(i) for i in con_ostr[:] if i != 0])

        return {'dsn':         dsn.value,
                'start_date':  sdate,
                'end_date':    edate,
                'LLSDAT':      LLSDAT[:],
                'LLEDAT':      LLEDAT[:],
                'tstep':       TSTEP.value,
                'tcode':       TCODE.value,
                'tcode_name':  MAPTCODE[TCODE.value],
                'location':    ostr.strip(),
                'scenario':    scen_ostr.strip(),
                'constituent': con_ostr.strip(),
                'tsfill':      TSFILL.value}

    def create_new_wdm(self, wdmpath, overwrite=False):
        ''' Create a new WDM fileronwfg
        '''
        if overwrite and os.path.exists(wdmpath):
            os.remove(wdmpath)
        elif os.path.exists(wdmpath):
            raise WDMFileExists(wdmpath)
        ronwfg = 2
        wdmfp = self.__open(wdmpath, ronwfg=ronwfg)
        self.__close(wdmpath)

    def create_new_dsn(self, wdmpath, dsn, tstype='', base_year=1900, tcode=4, tsstep=1, statid='', scenario='', location='', description='', constituent='', tsfill=-999.0):
        ''' Create self.wdmfp/dsn. '''
        wdmfp = self.__open(wdmpath)
        messfp = self.wmsgop()
        dsn = c_int(int(dsn))

        tstyp = self.wdckdt(byref(wdmfp), byref(dsn))
        if self.wdckdt(byref(wdmfp), byref(dsn)) == 1:
            raise DSNExistsError(dsn.value)

        # Parameters for wdlbax taken from ATCTSfile/clsTSerWDM.cls
        self.wdlbax(byref(wdmfp),
                    byref(dsn),
                    byref(c_int(1)),   # DSTYPE - always 1 for time series
                    byref(c_int(10)),  # NDN    - number of down pointers
                    byref(c_int(10)),  # NUP    - number of up pointers
                    byref(c_int(30)),  # NSA    - number of search attributes
                    byref(c_int(100)), # NSASP  - amount of search attribute space
                    byref(c_int(300)), # NDP    - number of data pointers
                    byref(c_int(1)))   # PSA    - pointer to search attribute space
        self.__retcode_check(RETCODE, additional_info='wdlbax')

        for saind, salen, val in [(34, 1, 6), #tgroup
                                  (83, 1, 1), #compfg
                                  (84, 1, 1), #tsform
                                  (85, 1, 1), #vbtime
                                  (17, 1, int(tcode)), #tcode
                                  (33, 1, int(tsstep)), #tsstep
                                  (27, 1, int(base_year)), #tsbyr
                                 ]:
            saind = c_int(saind)
            salen = c_int(salen)
            val = c_int(val)
            self.wdbsai(byref(wdmfp),
                        byref(dsn),
                        byref(messfp),
                        byref(saind),
                        byref(salen),
                        byref(val),
                        byref(RETCODE))
            self.__retcode_check(RETCODE, additional_info='wdbsai')

        for saind, salen, val in [(32, 1, tsfill)]: #tsfill
            saind = c_int(saind)
            salen = c_int(salen)
            val = c_float(val)
            self.wdbsar(byref(wdmfp),
                        byref(dsn),
                        byref(messfp),
                        byref(saind),
                        byref(salen),
                        byref(val),
                        byref(RETCODE))
            self.__retcode_check(RETCODE, additional_info='wdbsar')

        for saind, salen, val, error_name in [(2, 16, statid, 'Station ID'),
                                  (1, 4, tstype.upper(), 'Time series type - tstype'),
                                  (45, 48, description.upper(), 'Description'),
                                  (288, 8, scenario.upper(), 'Scenario'),
                                  (289, 8, constituent.upper(), 'Constituent'),
                                  (290, 8, location.upper(), 'Location'),
                                 ]:
            saind = c_int(saind)
            ostring = c_char * salen
            ostr = ostring()
            try:
                ostr.value = '{0:{1}}'.format(val, salen)
            except ValueError:
                raise ValueError('String "{0}" is too long for {1}.  Must have a length equal or less than {2}.'.format(val, error_name, salen))

            salen = c_int(salen)
            self.wdbsac(byref(wdmfp),
                        byref(dsn),
                        byref(messfp),
                        byref(saind),
                        byref(salen),
                        byref(RETCODE),
                        byref(ostr),
                        byref(salen))
            self.__retcode_check(RETCODE, additional_info='wdbsac')
        self.__close(wdmpath)

    def __tcode_date(self, tcode, date):
        ''' Uses tcode to set the significant parts of the date tuple. '''
        rdate = [0]*6
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
        import numpy.ma as ma

        wdmfp = self.__open(wdmpath)
        dsn_desc = self.describe_dsn(wdmpath, dsn)
        TCODE.value = dsn_desc['tcode']
        TSTEP.value = dsn_desc['tstep']

        LLSDAT[:] = self.__tcode_date(TCODE.value, (start_date.year, start_date.month, start_date.day, start_date.hour, start_date.minute, start_date.second))

        # Fill missing data with tsfill
        data = data.filled(dsn_desc['tsfill'])

        nvals = c_int(len(data))
        # Create array to hold the time series data
        arrsize = c_float * len(data)
        # Might be a better way, but this works....
        dataout = arrsize()
        dataout[:] = data
        self.wdtput(byref(wdmfp),
                    byref(c_int(dsn)),
                    byref(TSTEP),
                    byref(LLSDAT),
                    byref(nvals),
                    byref(c_int(1)),
                    byref(c_int(0)),
                    byref(TCODE),
                    byref(dataout),
                    byref(RETCODE))
        self.__retcode_check(RETCODE, additional_info='wdtput')
        self.__close(wdmpath)

    def read_dsn(self, wdmpath, dsn, start_date=None, end_date=None):
        ''' Read from a DSN.
        '''

        wdmfp = self.__open(wdmpath)
        # Call wdatim_ to get LLSDAT, LLEDAT, TSTEP, TCODE
        desc_dsn = self.describe_dsn(wdmpath, dsn)

        LLSDAT[:] = desc_dsn['LLSDAT']
        LLEDAT[:] = desc_dsn['LLEDAT']
        TCODE.value = desc_dsn['tcode']
        TSTEP.value = desc_dsn['tstep']

        dsn = c_int(int(dsn))
        self.__retcode_check(RETCODE, additional_info='wdatim')

        # These calls convert 24 to midnight of the next day
        self.timcvt(byref(LLSDAT))
        self.timcvt(byref(LLEDAT))

        if start_date != None:
            start_date = self.dateconverter(start_date).datetime.timetuple()[:6]
            LLSDAT[:] = start_date
        if end_date != None:
            end_date = self.dateconverter(end_date).datetime.timetuple()[:6]
            LLEDAT[:] = end_date

        # Determine the number of values (ITERM) from LLSDAT to LLEDAT
        self.timdif(byref(LLSDAT),
                    byref(LLEDAT),
                    byref(TCODE),
                    byref(TSTEP),
                    byref(ITERM))

        # Create array to hold the time series data
        arrsize = c_float * ITERM.value
        dataout = arrsize()

        # Get the data and put it into dictionary
        self.wdtget(byref(wdmfp),
                    byref(dsn),
                    byref(TSTEP),
                    byref(LLSDAT),
                    byref(ITERM),
                    byref(DTRAN),
                    byref(QUALFG),
                    byref(TCODE),
                    byref(dataout),
                    byref(RETCODE))
        self.__retcode_check(RETCODE, additional_info='wdtget')

        # Find the begining in datetime.datetime format
        tstart = datetime.datetime(LLSDAT[0],
                                   LLSDAT[1],
                                   LLSDAT[2],
                                   LLSDAT[3],
                                   LLSDAT[4],
                                   LLSDAT[5])

        self.__close(wdmpath)

        # Convert time series to scikits.timeseries object
        tmpval = ts.time_series(dataout,
                              start_date=ts.Date(MAPTCODE[TCODE.value], datetime=tstart),
                              freq = MAPTCODE[TCODE.value]
                              )
        return tmpval

    def read_dsn_por(self, wdmpath, dsn):
        ''' Read the period of record for a DSN.
        '''
        return self.read_dsn(wdmpath, dsn, start_date=None, end_date=None)

    def __close(self, wdmpath):
        ''' Close the WDM file.
        '''
        if wdmpath in self.openfiles:
            RETCODE.value = self.wdflcl(byref(self.openfiles[wdmpath]))
            self.__retcode_check(RETCODE, additional_info='wdflcl')
            toss = self.openfiles.pop(wdmpath)


if __name__ == '__main__':
    wdm_obj = WDM()
    fname = 'test.wdm'
    if os.name == 'nt':
        fname = r'c:\test.wdm'
    wdm_obj.create_new_wdm(fname, overwrite=True)
    listonumbers = [34.2, 35.0, 36.9, 38.2, 40.2 , 20.1, 18.4, 23.6]
    wdm_obj.create_new_dsn(fname, 1003, tstype='EXAM', scenario='OBSERVED', tcode=4, location='EXAMPLE')
    wdm_obj.write_dsn(fname, 1003, listonumbers, datetime.datetime(2000,1,1))
    print wdm_obj.read_dsn_por(fname, 1003)
