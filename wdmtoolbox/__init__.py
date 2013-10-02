#!/sjr/beodata/local/python_linux/bin/python
'''
'''
from __future__ import print_function

# Python batteries included imports
import sys
import datetime

# Third party imports
import baker
from dateutil.parser import parse as dateparser

# Local imports
# Load in WDM subroutines
import wdmtoolbox.wdmutil as wdmutil
import tsutils

wdm = wdmutil.WDM()

# Errors
class DSNDoesNotExist(Exception):
    pass

class FrequencyDoesNotMatchError(Exception):
    pass

class MissingValuesInInputError(Exception):
    pass


def _find_gcf(dividend, divisor):
    remainder = -1
    dividend = dividend.astype('i')
    divisor = divisor.astype('i')
    while remainder != 0:
        qoutient = dividend/divisor
        remainder = dividend%divisor
        if remainder != 0:
            dividend = divisor
            divisor = remainder
    gcf = divisor
    return divisor

# Foundation functions that allow other functions to print or use the returned
def _describedsn(wdmpath, dsn):
    try:
        return wdm.describe_dsn(wdmpath, int(dsn))
    except:
        return None

def _copy_dsn(inwdmpath, indsn, outwdmpath, outdsn):
    wdm.copydsnlabel(inwdmpath, indsn, outwdmpath, outdsn)
    nts = wdm.read_dsn(inwdmpath, indsn)
    wdm.write_dsn(outwdmpath, int(outdsn), nts.values, nts.index[0])

@baker.command
def copydsn(inwdmpath, indsn, outwdmpath, outdsn):
    ''' Make a copy of a DSN.
    :param inwdmpath: Path to input WDM file (<64 characters).
    :param indsn: Source DSN.
    :param outwdmpath: Path to clean copy WDM file (<64 characters).
    :param outdsn: Target DSN.
    '''
    _copy_dsn(inwdmpath, indsn, outwdmpath, outdsn)

@baker.command
def cleancopywdm(inwdmpath, outwdmpath, overwrite=False):
    ''' Make a clean copy of a WDM file.
    :param inwdmpath: Path to input WDM file (<64 characters).
    :param outwdmpath: Path to clean copy WDM file (<64 characters).
    :param overwrite: Whether to overwrite an existing outwdmpath.
    '''
    if inwdmpath == outwdmpath:
        raise ValueError('The "inwdmpath" cannot be the same as "outwdmpath"')
    createnewwdm(outwdmpath, overwrite=overwrite)
    activedsn = []
    for i in range(1,32001):
        try:
            activedsn.append(_describedsn(inwdmpath, i)['dsn'])
        except TypeError:
            continue
    # Copy labels then data
    for i in activedsn:
        _copy_dsn(inwdmpath, i, outwdmpath, i)


@baker.command
def renumberdsn(wdmpath, olddsn, newdsn):
    ''' Renumber olddsn to newdsn
    :param wdmpath: Path and WDM filename (<64 characters).
    :param olddsn: Old DSN to renumber.
    :param newdsn: New DSN to change old DSN to.
    '''
    wdm.renumber_dsn(wdmpath, olddsn, newdsn)

@baker.command
def deletedsn(wdmpath, dsn):
    ''' Delete DSN
    :param wdmpath: Path and WDM filename (<64 characters).
    :param dsn: DSN to delete.
    '''
    wdm.delete_dsn(wdmpath, dsn)

@baker.command
def wdmtoswmm5rdii(wdmpath, *dsns, **kwds):
    ''' Prints out DSN data to the screen in SWMM5 RDII format.
    :param wdmpath: Path and WDM filename (<64 characters).
    :param dsns:     The Data Set Numbers in the WDM file.
    :param start_date: If not given defaults to start of data set.
    :param end_date:   If not given defaults to end of data set.
    '''
    start_date = kwds.setdefault('start_date', None)
    end_date = kwds.setdefault('end_date', None)

    # Need to make sure that all DSNs are the same interval and all are within start and end dates.
    collect_tcodes = {}
    collect_tsteps = {}
    collect_keys = []
    for dsn in dsns:
        dsn_desc = _describedsn(wdmpath, dsn)
        collect_tcodes[dsn_desc['tcode']] = 1
        collect_tsteps[dsn_desc['tstep']] = 1
        if start_date:
            assert dateparser(start_date) >= dateparser(dsn_desc['start_date'])
        if end_date:
            assert dateparser(end_date) <= dateparser(dsn_desc['end_date'])
        collect_keys.append((dsn_desc['dsn'], dsn_desc['location']))
    assert len(collect_tcodes) == 1
    assert len(collect_tsteps) == 1

    collected_start_dates = []
    collected_end_dates = []
    collected_ts = {}
    for dsn, location in collect_keys:
        collected_ts[(dsn,location)] = wdm.read_dsn(wdmpath, int(dsn), start_date=start_date, end_date=end_date)
        collected_start_dates.append(collected_ts[(dsn,location)].dates[0])
        collected_end_dates.append(collected_ts[(dsn,location)].dates[-1])
    stdate = max(collected_start_dates)
    endate = min(collected_end_dates)

    MAPTCODE = {
        1: 1,
        2: 60,
        3: 3600,
        4: 86400,
        }

    print('SWMM5')
    print('RDII dump of DSNS {0} from {1}'.format(dsns, wdmpath))
    print(MAPTCODE[collect_tcodes.keys()[0]]*collect_tsteps.keys()[0])
    print(1)
    print('FLOW CFS')
    print(len(dsns))
    for dsn, location in collect_keys:
        print(str(dsn) + '_' + location)
    print('Node Year Mon Day Hr Min Sec Flow')
    # Can pick any time series because they should all have the same interval and start and end dates.
    for date in collected_ts[collect_keys[0]].dates:
        for dsn, location in collect_keys:
            print('{0}_{1}  {2}  {3:02}  {4:02}  {5:02}  {6:02}  {7:02}  {8:f}'.format(dsn, location, date.year, date.month, date.day, date.hour, date.minute, date.second, collected_ts[(dsn, location)][date]))

@baker.command
def wdmtostd(wdmpath, *dsns, **kwds): #start_date=None, end_date=None):
    ''' Prints out DSN data to the screen with ISO-8601 dates.
    :param wdmpath: Path and WDM filename (<64 characters).
    :param dsns:     The Data Set Numbers in the WDM file.
    :param start_date: If not given defaults to start of data set.
    :param end_date:   If not given defaults to end of data set.
    '''
    start_date = kwds.setdefault('start_date', None)
    end_date = kwds.setdefault('end_date', None)
    if len(kwds) > 2:
        kwds_list = kwds.keys()
        kwds_list.remove('start_date')
        kwds_list.remove('end_date')
        raise ValueError('The only allowed keywords are "--start_date=..." and "--end_date=...". You passed in {0}'.format(kwds_list))
    for index,dsn in enumerate(dsns):
        nts = wdm.read_dsn(wdmpath, int(dsn), start_date=start_date, end_date=end_date)
        if index == 0:
            result = nts
        else:
            result = result.join(nts, how='outer')
    tsutils.printiso(result)

@baker.command
def describedsn(wdmpath, dsn):
    ''' Prints out a description of a single DSN.
    :param wdmpath: Path and WDM filename (<64 characters).
    :param dsn:     The Data Set Number in the WDM file.
    '''
    print(_describedsn(wdmpath, dsn))

@baker.command
def listdsns(wdmpath):
    ''' Prints out a table describing all DSNs in the WDM.
    :param wdmpath: Path and WDM filename (<64 characters).
    '''
    print('#{0:<4} {1:>8} {2:>8} {3:>8} {4:<19} {5:<19} {6:>5} {7}'.format('DSN', 'SCENARIO', 'LOCATION', 'CONSTITUENT', 'START DATE', 'END DATE', 'TCODE', 'TSTEP'))
    for i in range(1,32001):
        testv = _describedsn(wdmpath, i)
        if testv:
            print('{dsn:5} {scenario:8} {location:8} {constituent:8}    {start_date:19} {end_date:19} {tcode_name:>5}({tcode}) {tstep}'.format(**testv))

@baker.command
def createnewwdm(wdmpath, overwrite=False):
    ''' Create a new WDM file, optional to overwrite.
    :param wdmpath: Path and WDM filename (<64 characters).
    :param overwrite: Defaults to not overwrite existing file.
    '''
    wdm.create_new_wdm(wdmpath, overwrite=overwrite)

@baker.command
def createnewdsn(wdmpath, dsn, tstype='', base_year=1900, tcode=4, tsstep=1, statid='', scenario='', location='', description='', constituent='', tsfill=-999.0):
    ''' Create a new DSN.
    :param wdmpath: Path and WDM filename (<64 characters).
    :param dsn: The Data Set Number in the WDM file.
    :param tstype: Time series type, defaults to ''.
    :param base_year: Base year of time series, defaults to 1900.
    :param tcode: Time series code, (1=second, 2=minute, 3=hour, 4=day, 5=month, 6= year) defaults to 4 = daily.
    :param tsstep: Time series steps, defaults (and almost always is) 1.
    :param statid: The station name, defaults to ''.
    :param scenario: The name of the the scenario, defaults to ''.
    :param location: The location, defaults to ''.
    :param description: Descriptive text, defaults to ''.
    :param constituent: The constituent that the time series represents, defaults to ''.
    :param tsfill: The value used as placeholder for missing values.
    '''
    wdm.create_new_dsn(wdmpath, int(dsn), tstype=tstype, base_year=base_year, tcode=tcode, tsstep=tsstep, statid=statid, scenario=scenario, location=location, description=description, constituent=constituent, tsfill=tsfill)

@baker.command
def hydhrseqtowdm(wdmpath, dsn, input=sys.stdin, start_century=1900):
    ''' Writes HYDHR sequential file to a DSN.
    :param wdmpath: Path and WDM filename (<64 characters).
    :param dsn: The Data Set Number in the WDM file.
    :param input: Input filename, defaults to standard input.
    :param start_century: Since 2 digit years are used, need century, defaults to 1900.
    '''
    dsn = int(dsn)
    import numpy as np
    if isinstance(input, basestring):
        input = open(input, 'r')
    dates = np.array([])
    data = np.array([])
    for line in input:
        words = line[8:]
        words = words.split()
        year = int(words[0]) + start_century
        month = int(words[1])
        day = int(words[2])
        ampmflag = int(words[3])
        if int(words[0]) == 99 and month == 12 and day == 31 and ampmflag == 2:
            start_century = start_century + 100
        data = np.append(data, [float(i) for i in words[4:16]])
        try:
            if ampmflag == 1:
                dates = np.append(dates, [datetime.datetime(year, month, day, i) for i in range(0,12)])
            if ampmflag == 2:
                dates = np.append(dates, [datetime.datetime(year, month, day, i) for i in range(12,24)])
                #dates = np.append(dates, datetime.datetime(year, month, day, 23) + datetime.timedelta(hours = 1))
        except ValueError:
            print(start_century, line)
    _writetodsn(wdmpath, dsn, dates, data)

@baker.command
def stdtowdm(wdmpath, dsn, infile='-'):
    ''' Writes data from a CSV file to a DSN.
    :param wdmpath: Path and WDM filename (<64 characters).
    :param dsn: The Data Set Number in the WDM file.
    :param infile: Input filename, defaults to standard input.
    '''
    tsd = tsutils.read_iso_ts(baker.openinput(infile))
    _writetodsn(wdmpath, dsn, tsd)

@baker.command
def csvtowdm(wdmpath, dsn, input=sys.stdin):
    ''' Writes data from a CSV file to a DSN.\n
    File can have comma separated\n
    'year', 'month', 'day', 'hour', 'minute', 'second', 'value'\n
    OR\n
    'date/time string', 'value'
    :param wdmpath: Path and WDM filename (<64 characters).
    :param dsn: The Data Set Number in the WDM file.
    :param input: Input filename, defaults to standard input.
    '''
    import numpy as np
    if isinstance(input, basestring):
        input = open(input, 'r')
    dates = np.array([])
    data = np.array([])
    for line in input:
        if '#' == line[0]:
            continue
        words = line.split(',')
        if len(words) == 2:
            if words[0]:
                dates = np.append(dates, dateparser(words[0], default=datetime.datetime(2000,1,1)))
                data = np.append(data, float(words[1]))
        elif len(words) == 7:
            for i in range(6):
                try:
                    words[i] = int(words[i])
                except ValueError:
                    words[i] = 0
            data = np.append(data, float(words[6]))
            dates = np.append(dates, datetime.datetime(*words[:6]))

    sorted_indices = np.argsort(dates)
    dates = dates[sorted_indices]
    data = data[sorted_indices]
    _writetodsn(wdmpath, dsn, dates, data)

def _writetodsn(wdmpath, dsn, data):
    # Convert string to int
    dsn = int(dsn)
    # Find ALL unique intervals in the data set and convert to seconds
    import numpy as np
    import numpy.ma as ma
    import pandas as pa

    interval = np.unique(data.index.values[1:] - data.index.values[:-1])
    interval = [np.timedelta64(i, 's') for i in interval]
    interval = np.array(interval)

    # If there are more than one interval lets see if the are caused by
    # missing values.  Say there is at least one 2 hour interval and at
    # least one 1 hour interval, this should correctly say the interval
    # is one hour.
    ninterval = {}
    if len(interval) > 1 and np.all(interval < np.timedelta64(28, 'D')):
        for i, aval in enumerate(interval):
            for j, bval in enumerate(interval[i+1:]):
                ninterval[_find_gcf(aval, bval)] = 1
        ninterval = ninterval.keys()
        ninterval.sort()
        interval = ninterval
    interval = interval[0]

    # Have the interval in seconds, need to convert to
    # interval identifier and calculate time step.
    interval = np.timedelta64(interval, 's').tolist()
    interval = interval.days*86400 + interval.seconds
    freq = 'A'
    tstep = 1
    if interval < 3600 and interval % 60 == 0:
        freq = 'T'
        tstep = interval/60
    elif interval < 86400 and interval % 3600 == 0:
        freq = 'H'
        tstep = interval/3600
    # The DAY and MONTH tests are not the best, could be fooled by day interval
    # with monthly/yearly time steps.
    elif interval not in 86400*np.array([28, 29, 30, 31, 365, 366]) and interval % 86400 == 0:
        freq = 'D'
        tstep = interval/86400
    elif interval in 86400*np.array([28, 29, 30, 31]):
        freq = 'M'
        tstep = int(round(interval/29.5))

    # Make sure that input data interval match target DSN
    desc_dsn = _describedsn(wdmpath, dsn)
    dsntcode = desc_dsn['tcode']
    if wdmutil.MAPFREQ[freq] != dsntcode:
        raise FrequencyDoesNotMatchError

    # Write the data...
    #data = pa.Series(data.values, data.index.values)
    # Eventually have to figure out why the following doesn't work...
    nindex = pa.date_range(data.index[0], data.index[-1],
            freq=data.index.inferred_freq)
    data = data.reindex(nindex.values, fill_value=-999)
    wdm.write_dsn(wdmpath, dsn, data.values, data.index[0])

def main():
    baker.run()

