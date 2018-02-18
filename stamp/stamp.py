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
import argparse
import re

from __init__ import __version__, STANDARD_COMPANY
from add import stamp_in
from end import stamp_out
from edit import edit_regex_resolver, edit_workday
from status import print_status, print_current_stamp
from export import create_pdf
from delete import delete_workday_or_tag
from tag import tag_stamp
from db import query_for_workdays, current_stamp


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


def add(args):
    stamp = stamp_in(args)
    return stamp


def end(args):
    stamp_out(args)
    return


def tag(args):
    if args.id == 'current':
        stamp = current_stamp()
    else:
        stamp = query_for_workdays(workday_id=int(args.id))

    stamp = tag_stamp(args.date, args.time, stamp, args.tag)
    return


def status(args):
    print_status(args)
    print_current_stamp()
    return


def export(args):
    create_pdf(args)
    return


def delete(args):
    if args.id == 'current':
        args.id = current_stamp().id
    else:
        args.id = int(args.id)
    delete_workday_or_tag(args.id, args.tag)
    return


# Edit only supports company for now
def edit(args):
    args.edit = edit_regex_resolver(args.edit)
    if args.id == 'current':
        args.id = current_stamp().id
    else:
        args.id = int(args.id)
    edit_workday(args)

    return


def version(*args, **kwargs):
    print(__version__)
    return


def main():
    # [Main parser]
    main_parser = argparse.ArgumentParser(description='''Register work hours.
                                          Hours get automatically sorted by date, and
                                          month is the default separator.''',
                                          epilog='''By arivarton
                                          (http://www.arivarton.com)''')
    main_parser.add_argument('-v', '--version', action='version', version=__version__,
                             help='Display current version.')

    # [Parent paramaters]

    # Date parameters
    date_parameters = argparse.ArgumentParser(add_help=False)
    date_parameters.add_argument('-D', '--date', type=lambda date: datetime.strptime(date, '%Y-%m-%d').date(), default=datetime.now().date(),
                                 help='Set date manually. Format is \'YYYY-mm-dd\' Default is now.')
    date_parameters.add_argument('-T', '--time', type=lambda time: datetime.strptime(time, '%H:%M').time(), default=datetime.now().time(),
                                 help='Set time manually. Default is now.')

    # Filter parameters
    filter_parameters = argparse.ArgumentParser(add_help=False)
    filter_parameters.add_argument('-f', '--filter', action='store_true',
                                   help='''Filter the output of status or pdf export. Use
                                   in combination with other arguments, f.ex status and company:
                                   "status -f -c MyCompany"''')

    # Company parameters
    company_parameters = argparse.ArgumentParser(add_help=False)
    company_parameters.add_argument('-c', '--company', type=str, default=STANDARD_COMPANY,
                                    help='Set company to bill hours to.')

    # [Subparsers]
    subparsers = main_parser.add_subparsers()

    # Add parser
    add_parser = subparsers.add_parser('add', help='''Add hours. If added with
                                       two separate times and/or dates the stamp
                                       will automaticall finish.''', parents=[date_parameters,
                                                                              company_parameters])
    add_parser.set_defaults(func=add)

    # End parser
    end_parser = subparsers.add_parser('end', help='End current stamp.',
                                       parents=[date_parameters,
                                                company_parameters])
    end_parser.set_defaults(func=end)

    # Tag parser
    tag_parser = subparsers.add_parser('tag', help='Tag a stamp.', parents=[date_parameters])
    tag_parser.add_argument('tag', type=str)
    tag_parser.add_argument('--id', type=str, default='current', help='''Choose
                               id to tag. Default is to tag current stamp.''')
    tag_parser.set_defaults(func=tag)

    # Status parser
    status_parser = subparsers.add_parser('status', help='Show registered hours.',
                                          parents=[filter_parameters,
                                                   company_parameters])
    status_parser.add_argument('-s', '--status', action='store_true',
                               help='Print current state of stamp.')
    status_parser.add_argument('-a', '--all', action='store_true',
                               help='Show status of all registered days.')
    status_parser.set_defaults(func=status)

    # Export parser
    export_parser = subparsers.add_parser('export', help='Export hours to file.',
                                          parents=[filter_parameters])
    export_parser.add_argument('type', type=str, choices=['pdf'])
    export_parser.set_defaults(func=export)

    # Delete parser
    delete_parser = subparsers.add_parser('delete', help='Delete a registered worktime.')
    delete_parser.add_argument('id', type=str, default='current', help='''Choose
                               id to delete (or to delete tag under).
                               Default is to delete current stamp.''')
    delete_parser.add_argument('-t', '--tag', type=int, help='''Choose tag id to
                               delete''')
    delete_parser.set_defaults(func=delete)

    # Edit parser
    edit_parser = subparsers.add_parser('edit', help='''Edit everything related to
                                        workdays or tags.''')
    edit_parser.add_argument('--id', type=str, default='current', help='''Workday
                             id to edit (or to edit the tags for). Default is
                             to edit current stamp.''')
    edit_parser.add_argument('-t', '--tag', type=int, help='Choose tag to edit.')
    edit_parser.add_argument('edit', type=str, help='''
                             Add edit message in this format:
                             "date=2018-02-18,comment='Changing this'".
                             Valid arguments: date, time, comment, company.
                             ''')
    edit_parser.set_defaults(func=edit)

    args = main_parser.parse_args()
    try:
        args.func(args)
    except AttributeError:
        main_parser.print_help()


if __name__ == '__main__':
    main()
