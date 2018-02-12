#!/usr/bin/env python3

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

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_SESSION = session()
STAMP_FILE = os.path.join(BASE_DIR, 'current_stamp.pickle')
HOURS = os.getenv('STAMP_HOURS') or '08:00-16:00'
LUNCH = os.getenv('STAMP_LUNCH') or '00:30'
MINIMUM_HOURS = int(os.getenv('STAMP_MINIMUM_HOURS') or 2)
STANDARD_COMPANY = os.getenv('STAMP_STANDARD_COMPANY') or 'Not specified'
WAGE_PER_HOUR = int(os.getenv('STAMP_WAGE_PER_HOUR') or 300)
CURRENCY = os.getenv('STAMP_CURRENCY') or 'NKR'

REPORT_DIR = os.getenv('STAMP_REPORT_DIR') or BASE_DIR


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
    hours, minutes = re.findall(r"[0-9]+", time)
    try:
        return datetime.time(datetime(1, 1, 1, int(hours), int(minutes)))
    except ValueError as error:
        print('Error in --time parameter:\n', error)


def _get_value_from_date_parameter(date):
    # Separate each part of date that user has put as argument
    # Argument could f.ex. look like this: 2017/02/20
    year, month, day = re.findall(r"[\d]+", date)
    try:
        return datetime.date(datetime(int(year), int(month), int(day)))
    except ValueError as error:
        print('Error in --date parameter:\n', error)


def _get_time_values(time):
    work_times = re.findall(r"([\d]+)[^\d]([\d]+)", time)
    if len(work_times) > 2:
        raise ValueError('Error in time parameter.')
    elif len(work_times) == 1:
        work_from = datetime.time(datetime(1, 1, 1, int(work_times[0][0]), int(work_times[0][1])))
        work_to = datetime.time(datetime(1, 1, 1, int(work_times[1][0]), int(work_times[1][1])))
    else:
        work_from = datetime.time(datetime(1, 1, 1, int(work_times[0][0]), int(work_times[0][1])))
        work_to = None
    return {'from': work_from, 'to': work_to}


def _determine_time_and_date(time, date, stamp_status):
    if date:
        workdate = _get_value_from_date_parameter(date)

    if time:
        worktime = _get_value_from_time_parameter(time)
    elif stamp_status == 'tag':
        worktime = datetime.now().time()
    else:
        _stamp_hours = _get_time_values(HOURS)
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
    total_wage = ((total_days*24) * WAGE_PER_HOUR) + (total_hours * WAGE_PER_HOUR)
    if minutes is 30:
        total_wage += WAGE_PER_HOUR * 0.5
    return total_days, total_hours, total_minutes, total_wage


def _output_for_total_hours_date_and_wage(workday):
    days, hours, minutes, wage = _determine_total_hours_worked_and_wage_earned(workday)
    output_total_wage = '%d%s' % (wage, CURRENCY)
    if days:
        output_total_hours = '%dd' % days
        if hours:
            output_total_hours += ', %dh' % hours
    else:
        output_total_hours = '%dh' % hours
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


def _query_db_for_workdays(workday_id=None, tag_id=None, args=None):
    try:
        if workday_id or tag_id:
            if tag_id:
                _workday = DB_SESSION.query(Workday).get(workday_id)
                workdays = _workday.tags.filter(Tag.id_under_workday == tag_id).all()
            else:
                workdays = [DB_SESSION.query(Workday).get(workday_id)]
        else:
            print(args)
            if args.filter:
                if args.company:
                    workdays = DB_SESSION.query(Workday).filter(Workday.company.ilike(args.company)).order_by(Workday.start)
                elif args['time'] and args['date']:
                    print('Not implemented yet')
                elif args['date']:
                    print('Not implemented yet')
                elif args['time']:
                    print('Not implemented yet')
            else:
                workdays = DB_SESSION.query(Workday).order_by(Workday.start)
    except exc.UnmappedInstanceError:
        print('Specified id not found')
    return workdays


def _delete_workday_or_tag(workday_id, tag_id):
    objects = _query_db_for_workdays(workday_id, tag_id)
    for workday in objects:
        DB_SESSION.delete(workday)
    DB_SESSION.commit()


def _edit_workday(args):
    objects = _query_db_for_workdays(workday_id=args['edit'])
    for workday in objects:
        if args['company']:
            workday.company = args['company']
        if args['time']:
            _edit_time = _get_time_values(args['time'])
            _stamped = _query_db_for_workdays(args['edit'])
            workday.start = datetime(_stamped[0].start.year, _stamped[0].start.month,
                                     _stamped[0].start.day, _edit_time['from'].hour,
                                     _edit_time['from'].minute)
            workday.end = datetime(_stamped[0].end.year, _stamped[0].end.month,
                                   _stamped[0].end.day, _edit_time['to'].hour,
                                   _edit_time['to'].minute)
    DB_SESSION.commit()


def _print_current_stamp():
    stamp = _current_stamp()
    if stamp is not None:
        print('\nCurrent stamp:')
        print('%s %s' % (stamp.start.date().isoformat(), stamp.start.time().isoformat()))
        print('Company: %s' % stamp.company)
        print('Tags: %d' % len(stamp.tags.all()))
        for tag in stamp.tags:
            print('%d: %s %s' % (tag.id_under_workday, tag.recorded.time().isoformat(), tag.tag))
    else:
        print('\nNot stamped in.')


def _print_status(args):
    workdays = _query_db_for_workdays(args=args)
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


def _stamp_in(args):
    date, time = _determine_time_and_date(args.time, args.date, 'in')
    stamp = Workday(start=datetime(date.year, date.month, date.day, time.hour, time.minute),
                    company=args['company'])
    print('Stamped in at %s - %s' % (date.isoformat(), time.isoformat()))
    return stamp


def _stamp_out(args):
    stamp = _current_stamp()
    date, time = _determine_time_and_date(args['time'], args['date'], 'out')
    stamp.end = datetime(date.year, date.month, date.day, time.hour, time.minute)
    DB_SESSION.add(stamp)
    DB_SESSION.commit()
    os.remove(STAMP_FILE)
    print('Stamped out at %s - %s' % (date.isoformat(), time.isoformat()))
    return


def _tag_stamp(date, time, stamp, tag):
    _id_under_workday = len(stamp.tags.all()) + 1
    stamp.tags.append(Tag(recorded=datetime(date.year, date.month, date.day, time.hour, time.minute),
                          tag=tag, id_under_workday=_id_under_workday))
    return stamp


def _create_pdf(args):
    workdays = _query_db_for_workdays(args=args)

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
    pdf.drawImage(os.path.join(BASE_DIR, 'logo.png'), width - 100, height - 110, width=100, height=100, mask=[0, 0, 0, 0, 0, 0])
    pdf.showPage()
    pdf.save()
    return


def add(args):
    stamp = _stamp_in(args)
    _write_pickle(stamp)
    return


def end(args):
    if args['company'] is not STANDARD_COMPANY:
        print('Company can only be set when stamping in')
    _stamp_out(args)
    return


def tag(args):
    stamp = _current_stamp()
    if args['company'] is not STANDARD_COMPANY:
        print('Company can only be set when stamping in')
    date, time = _determine_time_and_date(args['time'], args['date'], 'tag')
    stamp = _tag_stamp(date, time, stamp, args['tag'])
    _write_pickle(stamp)
    return


def status(args):
    _print_status(args)
    _print_current_stamp()
    return


def export(args):
    _create_pdf(args)
    return


def delete(args):
    _delete_workday_or_tag(args['delete'], args['tag'])
    return


# Edit only supports company for now
def edit(args):
    _edit_workday(args)
    return


def version():
    print(__version__)
    return


def main():
    # [Main parser]
    main_parser = argparse.ArgumentParser(description='''Register work hours.
                                          Hours get automatically sorted by date, and
                                          month is the default separator.''',
                                          epilog='''By arivarton
                                          (http://www.arivarton.com)''')
    main_parser.add_argument('-v', '--version', action='store_true',
                             help='Display current version.')

    # [Parent paramaters]

    # Date parameters
    date_parameters = argparse.ArgumentParser(add_help=False)
    date_parameters.add_argument('-D', '--date', type=str, default=str(datetime.now().date()),
                                 help='Set date manually. Default is now.')
    date_parameters.add_argument('-T', '--time', type=str, default=str(datetime.now().time()).split('.')[0],
                                 help='Set time manually. Default is now.')

    # Filter parameters
    filter_parameters = argparse.ArgumentParser(add_help=False)
    filter_parameters.add_argument('-f', '--filter', action='store_true',
                                   help='''Filter the output of status or pdf export. Use
                                   in combination with other arguments, f.ex status and company:
                                   "status -f -c MyCompany"''')

    # [Subparsers]
    subparsers = main_parser.add_subparsers()

    # Add parser
    add_parser = subparsers.add_parser('add', help='''Add hours. If added with
                                       two separate times and/or dates the stamp
                                       will automaticall finish.''', parents=[date_parameters])
    add_parser.add_argument('-c', '--company', type=str, default=STANDARD_COMPANY,
                            help='Set company to bill hours to.')
    add_parser.set_defaults(func=add)

    # End parser
    end_parser = subparsers.add_parser('end', help='End current stamp.',
                                       parents=[date_parameters])
    end_parser.set_defaults(func=end)

    # Tag parser
    tag_parser = subparsers.add_parser('tag', help='Tag a stamp.', parents=[date_parameters])
    tag_parser.set_defaults(func=tag)

    # Status parser
    status_parser = subparsers.add_parser('status', help='Show registered hours.',
                                          parents=[filter_parameters])
    status_parser.add_argument('-s', '--status', action='store_true',
                               help='Print current state of stamp.')
    status_parser.add_argument('-a', '--all', action='store_true',
                               help='Show status of all registered days.')
    status_parser.add_argument('-c', '--company', type=str,
                               help='Filter on company.')
    status_parser.set_defaults(func=status)

    # Export parser
    export_parser = subparsers.add_parser('export', help='Export hours to file.',
                                          parents=[filter_parameters])
    export_parser.add_argument('type', type=str, choices=['pdf'])
    export_parser.set_defaults(func=export)

    # Delete parser
    delete_parser = subparsers.add_parser('delete')
    delete_parser.add_argument('id', type=int)
    delete_parser.add_argument('-t', '--tag', type=int)
    delete_parser.set_defaults(func=delete)

    # Edit parser
    edit_parser = subparsers.add_parser('edit')
    edit_parser.add_argument('id', type=int)
    edit_parser.add_argument('-t', '--tag', type=int)
    edit_parser.set_defaults(func=edit)

    args = main_parser.parse_args()
    print(args.time)
    args.func(args)


if __name__ == '__main__':
    main()
