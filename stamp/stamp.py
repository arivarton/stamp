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
from sqlalchemy.orm import exc
from reportlab.pdfgen import canvas
from mappings import Workday, Tag, session
from __init__ import __version__
import argparse
import pickle
import re
import math
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_SESSION = session()
STAMP_FILE = os.path.join(BASE_DIR, 'current_stamp.pickle')
HOURS = os.getenv('STAMP_HOURS') or '08:00-16:00'
LUNCH = os.getenv('STAMP_LUNCH') or '00:30'
MINIMUM_HOURS = int(os.getenv('STAMP_MINIMUM_HOURS') or 2)
STANDARD_COMPANY = os.getenv('STAMP_STANDARD_COMPANY') or 'Not specified'
WAGE_PER_HOUR = int(os.getenv('STAMP_WAGE_PER_HOUR') or 300)
CURRENCY = os.getenv('STAMP_CURRENCY') or 'NKR'

REPORT_DIR = os.getenv('STAMP_REPORT_DIR') or BASE_DIR


def get_parser():
    parser = argparse.ArgumentParser(description='''Register work hours.
                                     Hours get automatically sorted by date, and
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
                        help='''Set time manually. Use the keyword "current" to
                        use current time instead of time specified by the HOURS
                        variable.''')
    parser.add_argument('-c', '--company', type=str, default=STANDARD_COMPANY,
                        help='Set company to bill hours to.')
    parser.add_argument('-s', '--status', action='store_true',
                        help='Print current state of stamp.')
    parser.add_argument('-e', '--export', action='store_true',
                        help='Export as PDF.')
    parser.add_argument('-d', '--delete', type=int,
                        help='Delete the specified id. To delete a tag inside a \
                        workday, add the workday id and the tag parameter with \
                        the tag id to delete. F.ex. "-d 3 -t 4".', default=False)
    parser.add_argument('-v', '--version', action='store_true',
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


def _determine_total_hours_worked_and_wage_earned(workdays):
    # If workdays is an object (Workday) it must be put in a list
    try:
        workdays = list(workdays)
    except TypeError:
        workdays = [workdays]
    total_days = 0
    total_hours = 0
    total_minutes = 0
    total_wage = 0
    for workday in workdays:
        total = workday.end - workday.start
        hours = total.seconds / 3600
        total_days += total.days
        # Rounds up hours
        if round(hours) == math.ceil(hours):
            minutes = 0
        else:
            minutes = 30
        # If total work time is under MINIMUM_HOURS then set work time to
        # MINIMUM_HOURS instead
        if total.days is 0 and hours < MINIMUM_HOURS:
            hours = MINIMUM_HOURS
            total_hours += hours
            minutes = 0
        else:
            hours = round(hours)
            total_hours += hours
        # Increment hour if minutes has passed 60
        if minutes is 30 and total_minutes is 30:
            total_hours += 1
            total_minutes = 0
        total_minutes = minutes
        # Increment days if total hours has passed 23
        if total_hours >= 24:
            total_days += 1
            total_hours -= 24
        # Add to wage
        total_wage += ((total_days*24) * WAGE_PER_HOUR) + (hours * WAGE_PER_HOUR)
        if minutes is 30:
            total_wage += WAGE_PER_HOUR * 0.5
    return total_days, total_hours, total_minutes, total_wage


def _output_for_total_hours_date_and_wage(workday):
    days, hours, minutes, wage = _determine_total_hours_worked_and_wage_earned(workday)
    output_total_hours = '%dh' % hours
    output_total_wage = '%d%s' % (wage, CURRENCY)
    if days:
        output_total_hours = '%dd, %dh' % (days, hours)
    if minutes:
        output_total_hours += ', %dm' % minutes
    # Add output date if the workday is not a list
    # If workday is a list, then it means total hours are being calculated
    # and the date is unneccesary
    try:
        if workday.start.date() == workday.end.date():
            output_date = workday.start.date().isoformat()
        else:
            output_date = '%s-%s' % (workday.start.date().isoformat(),
                                     workday.end.date().isoformat())
    except AttributeError:
        output_date = None
    return output_total_hours, output_date, output_total_wage


def _query_db_for_workdays():
    workdays = DB_SESSION.query(Workday).order_by(Workday.start)
    return workdays


def _query_db_and_print_status():
    workdays = _query_db_for_workdays()
    for workday in workdays:
        output_total_hours, output_date, output_total_wage = _output_for_total_hours_date_and_wage(workday)
        print('id: %d' % workday.id)
        print(output_date)
        print('Company: %s' % workday.company)
        print('Workday: ')
        print('%s-%s' % (workday.start.time().isoformat(),
                         workday.end.time().isoformat()))
        print('Hours: %s@%s' % (output_total_hours, output_total_wage))
        print('Tags: %d' % len(workday.tags.all()))
        for tag in workday.tags:
            print('%d: %s %s' % (tag.id_under_workday, tag.recorded.time().isoformat(), tag.tag))
        print('--')
    output_total_hours, __, output_total_wage = _output_for_total_hours_date_and_wage(workdays)
    print('Total hours: %s' % output_total_hours)
    print('Total wage earned: %s' % output_total_wage)


def _query_db_and_delete(workday_id, tag_id):
    try:
        if tag_id:
            _workday = DB_SESSION.query(Workday).get(workday_id)
            objects = _workday.tags.filter(Tag.id_under_workday == tag_id).all()
        else:
            objects = [DB_SESSION.query(Workday).get(workday_id)]
        for object in objects:
            DB_SESSION.delete(object)
        DB_SESSION.commit()
    except exc.UnmappedInstanceError:
        print('Specified id to delete not found')


def _print_current_stamp():
    stamp = _current_stamp()
    if stamp is not None:
        print('\nCurrent stamp:')
        print('%s %s' % (stamp.start.date().isoformat(), stamp.start.time().isoformat()))
        print('Tags: %d' % len(stamp.tags.all()))
        for tag in stamp.tags:
            print('%d: %s %s' % (tag.id_under_workday, tag.recorded.time().isoformat(), tag.tag))
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
    _id_under_workday = len(stamp.tags.all()) + 1
    stamp.tags.append(Tag(recorded=datetime(date.year, date.month, date.day, time.hour, time.minute),
                          tag=tag, id_under_workday=_id_under_workday))
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


def _create_pdf():
    workdays = _query_db_for_workdays()

    output_filename = os.path.join(REPORT_DIR, 'report.pdf')

    # A4 paper, 210mm*297mm displayed on a 96dpi monitor
    width = 210 / 25.4 * 96
    height = 297 / 25.4 * 96

    pdf = canvas.Canvas(output_filename, pagesize=(width, height))
    pdf.setStrokeColorRGB(0, 0, 0)
    pdf.setFillColorRGB(0, 0, 0)
    font_size = 12
    font_padding = 20
    pdf.setFont("Helvetica", font_size)
    height_placement = height - font_size
    for workday in workdays:
        output_hours, output_date, output_wage = _output_for_total_hours_date_and_wage(workday)
        height_placement -= font_size
        # Date
        pdf.drawString(font_padding, height_placement, '%s %s-%s' % (output_date,
                                                                     workday.start.time().isoformat(),
                                                                     workday.end.time().isoformat()))
        height_placement -= font_size
        # Worktime
        pdf.drawImage(os.path.join(BASE_DIR, 'logo.png'), width - 100, height - 110, width=100, height=100, mask=[0, 0, 0, 0, 0, 0])
        pdf.drawString(font_padding, height_placement, 'Total hours: %s' % (output_hours))
        height_placement -= font_size
        pdf.drawString(font_padding, height_placement, 'Wage: %s' % (output_wage))
        for tag in workday.tags:
            height_placement -= font_size
            pdf.drawString(font_padding, height_placement, '%s - %s' % (tag.recorded.time().isoformat(), tag.tag))
        height_placement -= font_size
    output_total_hours, __, output_total_wage = _output_for_total_hours_date_and_wage(workdays)
    height_placement -= font_size * 2
    pdf.drawString(font_padding, height_placement, 'Total hours: %s' % (output_total_hours))
    height_placement -= font_size
    pdf.drawString(font_padding, height_placement, 'Total wage: %s' % (output_total_wage))
    pdf.showPage()
    pdf.save()
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
        _create_pdf()
        return  # NEED TO EXPORT TO PDF HERE

    if args['delete']:
        _query_db_and_delete(args['delete'], args['tag'])
        return

    _stamp_or_tag(args)

if __name__ == '__main__':
    run()
