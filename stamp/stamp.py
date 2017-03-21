#!/usr/bin/env python

##############################
#
#    Stamp in before starting
#    the workday, tag
#    points in time with
#    comments and stamp out
#    when workday is over.
#
##############################

from datetime import datetime
from . import __version__
import logging
import argparse
import pickle
import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
STAMP_FILE = os.path.join(BASE_DIR, 'current_stamp.pickle')
HOURS = os.getenv('STAMP_HOURS') or '08:00-16:00'


def get_parser():
    parser = argparse.ArgumentParser(description='''Register work hours.
                                     Hours get automatically sorted by date and
                                     month is the default separator.''',
                                     epilog='''By arivarton
                                     (http://www.arivarton.com)''')
    parser.add_argument('-t', '--tag', type=str, default=False,
                        help='''Tag new or current (if already initalized)
                        stamp with a comment. Marked with current time or
                        time specified by the date argument.''')
    parser.add_argument('-D', '--date', type=str, default=False,
                        help='Set date manually.')
    parser.add_argument('-T', '--time', type=str, default=False,
                        help='Set time manually.')
    parser.add_argument('-s', '--status', action='store_true',  # Finished
                        help='Print current state of stamp.')
    parser.add_argument('-e', '--export', type=str,
                        help='Export as PDF.', default=False)
    parser.add_argument('-v', '--version', action='store_true',  # Finished
                        help='Display current version.')
    return parser


def _write_pickle(stamp):
    pickle.dump(stamp, open(STAMP_FILE), 'wb')


def _current_stamp():
    if os.path.isfile(STAMP_FILE):
        stamp = pickle.open(STAMP_FILE, 'rb')
    else:
        stamp = None
    return stamp


def _get_value_from_time_parameter(time):
    # Separate each part of time that user has put as argument
    # Argument could f.ex. look like this: 16:45
    hours, minutes = re.findall(r"[\w]+", time)
    try:
        return datetime.time(datetime(1, 1, 1, int(hours), int(minutes)))
    except ValueError as error:
        print('Error in --time parameter:\n', error)


def _get_value_from_date_parameter(date):
    # Separate each part of date that user has put as argument
    # Argument could f.ex. look like this: 2017/02/20
    year, month, day = re.findall(r"[\w]+", date)
    try:
        return datetime.date(datetime(int(year), int(month), int(day)))
    except ValueError as error:
        print('Error in --date parameter:\n', error)


def _get_values_from_stamp_hours_variable():
    _work_from, _work_to = re.findall(r"([\w]+).([\w]+)", HOURS)
    try:
        work_from = datetime.time(datetime(1, 1, 1, _work_from[0], _work_from[1]))
        work_to = datetime.time(datetime(1, 1, 1, _work_to[0], _work_to[1]))
    except ValueError as error:
        print('Error in STAMP_HOURS environment variable:\n', error)
    return {'from': work_from, 'to': work_to}


def _determine_work_hour(time, date, stamp_status):
    if date:
        workdate = _get_value_from_date_parameter(date)
    else:
        workdate = datetime.now().date()

    if time == 'current':
        worktime = datetime.now().time()
    elif time:
        worktime = _get_value_from_time_parameter(time)
    else:
        _stamp_hours = _get_values_from_stamp_hours_variable()
        if stamp_status == 'in':
            worktime = _stamp_hours['from']
        elif stamp_status == 'out':
            worktime = _stamp_hours['to']
    return workdate, worktime

def _stamp_in(date, time):
    return {'start': {'date': date, 'time': time}, 'tags': {}}


def _stamp_out(date, time, stamp):
    stamp.update({'end': {'date': date, 'time': time})
    # Add stamp to database
    # Delete stamp file
    return


def _create_stamp(args):
    stamp = _current_stamp()

    # Stamp out
    if stamp is not None and args['tag'] is False:
        date, time = _determine_work_hour(args['time'], args['date'], 'out')
        _stamp_out(date, time, stamp)
    # Tag
    elif args['tag']:
        stamp['tags'].update({'date': date, 'time': time, 'tag': args['tag']})
        _write_pickle(stamp)
    # Stamp in
    else:
        date, time = _determine_work_hour(args['time'], args['date'], 'in')
        stamp = _stamp_in(date, time)
        _write_pickle(stamp)

    return


def run():
    parser = get_parser()
    args = vars(parser.parse_args())

    if args['version']:
        print(__version__)
        return

    if args['status']:
        return  ### NEED TO PRINT THE STATUS HERE ###

    if args['export']:
        return  ### NEED TO EXPORT TO PDF HERE ###

    _create_stamp(args)

if __name__ == '__main__':
    run()
