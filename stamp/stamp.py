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
    parser.add_argument('-d', '--datetime', type=str, default=False,
                        help='Set date and time manually.')
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

def _separate_values_from_datetime(datetime):
    # Separate each part of datetime that user has put as argument
    # Argument could f.ex. look like this: 2017/02/20, 20:32:10
    year, month, day, *usertime = re.findall(r"[\w']+", datetime)
    time = ['0'] * 3
    for index, value in usertime:
        time[index] = value
    try:
        return datetime(int(year), int(month), int(day),
                        int(time[0]), int(time[1]), int(time[2]))
    except ValueError as error:
        print('Error in --date parameter:\n', error)

def _separate_values_from_hours(date):
    _work_from, _work_to = re.findall(r"([\w']+):([\w]+)", HOURS)
    work_from = datetime(

def _stamp_in(date, hours):
    # Do you want to register standard hours or current time as start?
    return {'start': date, 'hours': hours, 'tags': {}}

def _stamp_out(stamp):
    # Do you want to register standard hours or current time as end?
    stamp.update({'end': args['date']})
    # Add stamp to database
    # Delete stamp file
    return

def _create_stamp(args):
    stamp = _current_stamp()

    if args['datetime']:
        date = _separate_values_from_datetime(args['datetime'])
    else:
        date = datetime.now()

    if stamp is not None and args['tag'] is False:
        _stamp_out(stamp)
    elif args['tag']:
        stamp['tags'].update({date: args['tag']})
        _write_pickle(stamp)
    else:
        hours = _separate_values_from_hours()
        stamp = _stamp_in(date, hours)
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
