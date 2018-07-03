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


import argparse
import sys
import os

from . import __version__
from .settings import STANDARD_CUSTOMER, STANDARD_PROJECT, DATA_DIR, DB_FILE
from .add import stamp_in
from .end import stamp_out
from .edit import edit_regex_resolver, edit_workday
from .status import print_status, print_current_stamp, print_invoices
from .delete import delete_workday_or_tag
from .tag import tag_stamp
from .db import Database
from .export import export_invoice
from .exceptions import (NoMatchingDatabaseEntryError, CurrentStampNotFoundError,
                         NoMatchesError, TooManyMatchesError)
from .args_helpers import DateAction, TimeAction


def add(args):
    stamp = stamp_in(args)
    return stamp


def end(args):
    try:
        stamp_out(args)
    except CurrentStampNotFoundError as _err_msg:
        print(_err_msg)
        sys.exit(0)
    return True


def tag(args):
    db = Database(args.db)
    if args.id == 'current':
        try:
            stamp = db.current_stamp()
        except CurrentStampNotFoundError as _err_msg:
            print(_err_msg)
    else:
        stamp = db.query_for_workdays(workday_id=int(args.id))

    stamp = tag_stamp(args.date, args.time, stamp, args.tag, db.session)
    return True


def status(args):
    db = Database(args.db)
    try:
        if args.invoices:
            print_invoices(db.get_invoices(args.show_superseeded))
        else:
            status_query = db.query_for_workdays(args=args)
            print_status(status_query)
    except NoMatchingDatabaseEntryError as _err_msg:
        print(_err_msg)
    try:
        print(print_current_stamp(db.current_stamp()))
    except CurrentStampNotFoundError as _err_msg:
        print(_err_msg)
    return True


def export(args):
    db = Database(args.db)
    try:
        return export_invoice(db, args.year, args.month, args.customer,
                              args.project, args.pdf)
    except NoMatchingDatabaseEntryError as _err_msg:
        print(_err_msg)
        sys.exit(0)
    except TooManyMatchesError as _err_msg:
        print(_err_msg)
        sys.exit(0)
    except NoMatchesError as _err_msg:
        print(_err_msg)
        sys.exit(0)
    db.session.commit()


def delete(args):
    db = Database(args.db)
    if args.id == 'current':
        try:
            args.id = db.current_stamp().id
        except CurrentStampNotFoundError as _err_msg:
            print(_err_msg)
    else:
        args.id = int(args.id)
    delete_workday_or_tag(args.id, args.tag, db)
    return


# Edit only supports customer for now
def edit(args):
    db = Database(args.db)
    args.edit = edit_regex_resolver(args.edit)
    if args.id == 'current':
        try:
            args.id = db.current_stamp().id
        except CurrentStampNotFoundError as _err_msg:
            print(_err_msg)
    else:
        args.id = int(args.id)
    edit_workday(args.id, args.edit, db)

    return


def parse_args(args):
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
    date_parameters.add_argument('-D', '--date', action=DateAction)
    date_parameters.add_argument('-T', '--time', action=TimeAction)

    # Filter parameters
    filter_parameters = argparse.ArgumentParser(add_help=False)
    filter_parameters.add_argument('-f', '--filter', action='store_true',
                                   help='''Filter the output of status or pdf export.
                                   Use this format:
                                   "date_from=2018-02-18,date_to=2018-04-20,
                                   company='somecompany'".''')

    # Company parameters
    customer_parameters = argparse.ArgumentParser(add_help=False)
    customer_parameters.add_argument('-c', '--customer', type=str, default=STANDARD_CUSTOMER,
                                     help='Set customer to bill hours to.')

    # Project parameters
    project_parameters = argparse.ArgumentParser(add_help=False)
    project_parameters.add_argument('-p', '--project', type=str, default=STANDARD_PROJECT,
                                    help='Set the project to add hours to.')

    # Database parameters
    db_parameters = argparse.ArgumentParser(add_help=False)
    db_parameters.add_argument('-d', '--db', type=lambda db_name: os.path.join(DATA_DIR, db_name) + '.db',
                               default=os.path.join(DATA_DIR, DB_FILE),
                               help='Choose database name.')

    # [Subparsers]
    subparsers = main_parser.add_subparsers()

    # Add parser
    in_parser = subparsers.add_parser('in', help='''Add stamp. If added with
                                       two separate times and/or dates the stamp
                                       will automatically finish.''',
                                      parents=[date_parameters,
                                               customer_parameters,
                                               project_parameters,
                                               db_parameters])
    in_parser.set_defaults(func=add)

    # End parser
    out_parser = subparsers.add_parser('out', help='End current stamp.',
                                       parents=[date_parameters,
                                                db_parameters])
    out_parser.set_defaults(func=end)

    # Tag parser
    tag_parser = subparsers.add_parser('tag', help='Tag a stamp.',
                                       parents=[date_parameters,
                                                db_parameters])
    tag_parser.add_argument('tag', type=str)
    tag_parser.add_argument('--id', type=str, default='current', help='''Choose
                               id to tag. Default is to tag current stamp.''')
    tag_parser.set_defaults(func=tag)

    # Status parser
    status_parser = subparsers.add_parser('status', help='Show registered hours.',
                                          parents=[filter_parameters,
                                                   customer_parameters,
                                                   project_parameters,
                                                   db_parameters])
    status_parser.add_argument('--invoices',
                               action='store_true',
                               help='Show status of invoices.')
    status_parser.add_argument('-s', '--show_superseeded',
                               action='store_true',
                               help='Show all created invoices. Only valid with the invoices option.')
    status_parser.set_defaults(func=status)

    # Export parser
    export_parser = subparsers.add_parser('export', help='Export hours to file.',
                                          parents=[filter_parameters,
                                                   db_parameters])
    export_parser.add_argument('month', type=str)
    export_parser.add_argument('year', type=str)
    export_parser.add_argument('customer', type=str)
    export_parser.add_argument('-p', '--pdf', action='store_true',
                               help='Export to PDF.')
    export_parser.add_argument('project', type=str, nargs='?')
    export_parser.set_defaults(func=export)

    # Delete parser
    delete_parser = subparsers.add_parser('delete',
                                          help='Delete a registered worktime.',
                                          parents=[db_parameters])
    delete_parser.add_argument('--id', type=str, default='current', help='''Choose
                               id to delete (or to delete tag under).
                               Default is to delete current stamp.''')
    delete_parser.add_argument('-t', '--tag', type=int, help='''Choose tag id to
                               delete''')
    delete_parser.set_defaults(func=delete)

    # Edit parser
    edit_parser = subparsers.add_parser('edit', help='''Edit everything related to
                                        workdays or tags.''',
                                        parents=[db_parameters])
    edit_parser.add_argument('--id', type=str, default='current', help='''Workday
                             id to edit (or to edit the tags for). Default is
                             to edit current stamp.''')
    edit_parser.add_argument('-t', '--tag', type=int, help='Choose tag to edit.')
    edit_parser.add_argument('edit', type=str, help='''
                             Add edit message in this format:
                             "date=2018-02-18,comment='Changing this'".
                             Valid arguments: date, time, comment, customer.
                             ''')
    edit_parser.set_defaults(func=edit)

    return main_parser.parse_args(args)


def main():
    parser = parse_args(sys.argv[1:])
    if vars(parser):
        parser.func(parser)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
