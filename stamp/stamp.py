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
from mappings import Workday, Tag, session
from __init__ import __version__
import argparse
import pickle
import os
import re
import math

DB_SESSION = session()
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
STAMP_FILE = os.path.join(BASE_DIR, 'current_stamp.pickle')
HOURS = os.getenv('STAMP_HOURS') or '08:00-16:00'
LUNCH = os.getenv('STAMP_LUNCH') or '00:30'
MINIMUM_HOURS = os.getenv('STAMP_MINIMUM_HOURS') or '2'
STANDARD_COMPANY = os.getenv('STAMP_STANDARD_COMPANY') or 'Not specified'


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
    parser.add_argument('-c', '--company', type=str, default=STANDARD_COMPANY,
                        help='Set company to bill hours to.')
    parser.add_argument('-s', '--status', action='store_true',  # Finished
                        help='Print current state of stamp.')
    parser.add_argument('-e', '--export', type=str,
                        help='Export as PDF.', default=False)
    parser.add_argument('-v', '--version', action='store_true',  # Finished
                        help='Display current version.')
    return parser


def _write_pickle(stamp):
    with open(STAMP_FILE, 'wb') as stamp_file:
        pickle.dump(stamp, stamp_file)
    return


def _current_stamp():
    if os.path.isfile(STAMP_FILE):
        with open(STAMP_FILE, 'rb') as stamp_file:
            stamp = pickle.load(stamp_file)
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
        work_from = datetime.time(datetime(1, 1, 1, int(_work_from[0]), int(_work_from[1])))
        work_to = datetime.time(datetime(1, 1, 1, int(_work_to[0]), int(_work_to[1])))
    except ValueError as error:
        print('Error in STAMP_HOURS environment variable:\n', error)
    return {'from': work_from, 'to': work_to}


def _determine_time_and_date(time, date, stamp_status):
    if date:
        workdate = _get_value_from_date_parameter(date)
    else:
        workdate = datetime.now().date()

    if time == 'current':
        worktime = datetime.now().time()
    elif time:
        worktime = _get_value_from_time_parameter(time)
    elif stamp_status == 'tag':
        worktime = datetime.now().time()
    else:
        _stamp_hours = _get_values_from_stamp_hours_variable()
        if stamp_status == 'in':
            worktime = _stamp_hours['from']
        elif stamp_status == 'out':
            worktime = _stamp_hours['to']
    return workdate, worktime


def _determine_total_hours_worked(workday):
    total = workday.end - workday.start
    hours = total.seconds / 3600
    if round(hours) == math.ceil(hours):
        minutes = 0
    else:
        minutes = 30
    if total.days is 0 and hours < int(MINIMUM_HOURS):
        hours = int(MINIMUM_HOURS)
        minutes = 0
    return total.days, round(hours), minutes


def _query_db_and_print_status():
    for workday in DB_SESSION.query(Workday).order_by(Workday.start):
        days, hours, minutes = _determine_total_hours_worked(workday)
        if days:
            output_total_hours = (str(days) + 'd, ' +
                                  str(hours) + 'h')
        else:
            output_total_hours = (str(hours) + 'h')
        if minutes:
            output_total_hours += ', ' + str(minutes) + 'm'
        if workday.start.date() == workday.end.date():
            output_date = workday.start.date().isoformat()
        else:
            output_date = (workday.start.date().isoformat() + '-' +
                           workday.end.date().isoformat())
        print('id: ' + str(workday.id))
        print(output_date)
        print('Company: ' + workday.company)
        print('Workday: ')
        print(workday.start.time().isoformat() + '-' +
              workday.end.time().isoformat())
        print('Total hours: ' + output_total_hours)
        print('Tags: ' + str(len(workday.tags)))
        for tag in workday.tags:
            print(tag.recorded.time().isoformat() + ' ' + tag.tag)
        print('--')


def _print_current_stamp():
    stamp = _current_stamp()
    if stamp is not None:
        print('\nCurrent stamp:')
        print(stamp.start.date().isoformat() + ' ' + stamp.end.time().isoformat())
        print('Tags: ' + str(len(stamp.tags)))
        for tag in stamp.tags:
            print(tag.recorded.time().isoformat() + ' ' + tag.tag)
    else:
        print('\nNot stamped in.')


def _stamp_in(date, time, company):
    stamp = Workday(start=datetime(date.year, date.month, date.day, time.hour, time.minute),
                    company=company)
    return stamp


def _stamp_out(date, time, stamp):
    stamp.end = datetime(date.year, date.month, date.day, time.hour, time.minute)
    DB_SESSION.add(stamp)
    DB_SESSION.commit()
    os.remove(STAMP_FILE)
    return


def _tag_stamp(date, time, stamp, tag):
    stamp.tags.append(Tag(recorded=datetime(date.year, date.month, date.day, time.hour, time.minute),
                          tag=tag))
    return stamp


def _stamp_or_tag(args):
    stamp = _current_stamp()

    # Stamp out
    if stamp is not None and args['tag'] is False:
        if args['company'] is not STANDARD_COMPANY:
            print('Company can only be set when stamping in')
        date, time = _determine_time_and_date(args['time'], args['date'], 'out')
        _stamp_out(date, time, stamp)
    # Tag
    elif stamp is not None and args['tag']:
        if args['company'] is not STANDARD_COMPANY:
            print('Company can only be set when stamping in')
        date, time = _determine_time_and_date(args['time'], args['date'], 'tag')
        stamp = _tag_stamp(date, time, stamp, args['tag'])
        _write_pickle(stamp)
    # Stamp in
    else:
        date, time = _determine_time_and_date(args['time'], args['date'], 'in')
        stamp = _stamp_in(date, time, args['company'])
        if args['tag']:
            stamp = _tag_stamp(date, time, stamp, args['tag'])
        _write_pickle(stamp)

    return


def run():
    parser = get_parser()
    args = vars(parser.parse_args())

    if args['version']:
        print(__version__)
        return

    if args['status']:
        _query_db_and_print_status()
        _print_current_stamp()
        return

    if args['export']:
        return  # NEED TO EXPORT TO PDF HERE

    _stamp_or_tag(args)

if __name__ == '__main__':
    run()
