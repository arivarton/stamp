import os
import argparse

from . import __version__
from .args_helpers import DateAction, TimeAction
from .main import add, end, tag, status, export, delete, edit

from .settings import STANDARD_CUSTOMER, STANDARD_PROJECT, DATA_DIR, DB_FILE


def parse(args):
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
    filter_parameters.add_argument('--date_from')
    filter_parameters.add_argument('--date_to')
    filter_parameters.add_argument('--time_from')
    filter_parameters.add_argument('--time_to')

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
    db_parameters.add_argument('--db', type=lambda db_name: os.path.join(DATA_DIR, db_name) + '.db',
                               default=os.path.join(DATA_DIR, DB_FILE),
                               help='Choose database name.')

    # [Subparsers]
    main_subparsers = main_parser.add_subparsers()

    # Add parser
    in_parser = main_subparsers.add_parser('in', aliases=['i'],
                                           help='''Add stamp. If added with
                                           two separate times and/or dates the stamp
                                           will automatically finish.''',
                                      parents=[date_parameters,
                                               customer_parameters,
                                               project_parameters,
                                               db_parameters])
    in_parser.set_defaults(func=add)

    # End parser
    out_parser = main_subparsers.add_parser('out', aliases=['o'],
                                            help='End current stamp.',
                                            parents=[date_parameters,
                                            db_parameters])
    out_parser.set_defaults(func=end)

    # Tag parser
    tag_parser = main_subparsers.add_parser('tag', aliases=['t'],
                                            help='Tag a stamp.',
                                       parents=[date_parameters,
                                                db_parameters])
    tag_parser.add_argument('tag', type=str)
    tag_parser.add_argument('--id', type=str, default='current', help='''Choose
                               id to tag. Default is to tag current stamp.''')
    tag_parser.set_defaults(func=tag)

    # Status parser
    status_parser = main_subparsers.add_parser('status', aliases=['s'],
                                               help='Show registered hours.',
                                          parents=[filter_parameters,
                                                   customer_parameters,
                                                   project_parameters,
                                                   db_parameters])
    status_parser.set_defaults(func=status, parser_object=status_parser.prog)

    status_subparsers = status_parser.add_subparsers()
    status_invoices_parser = status_subparsers.add_parser('invoices', aliases=['i'],
                                                          help='Show status of invoices.',
                                                          parents=[db_parameters,
                                                                   date_parameters])
    status_invoices_parser.add_argument('-i', '--invoice_id', type=int,
                                        help='Only show invoice with specified id.')
    status_invoices_parser.add_argument('-s', '--show_superseeded',
                                        action='store_true',
                                        help='''Show all created invoices including
                                        superseeded.''')
    status_invoices_parser.set_defaults(func=status, parser_object=status_invoices_parser.prog)
    status_workdays_parser = status_subparsers.add_parser('workdays', aliases=['w'],
                                                          help='Show status of workdays.',
                                                          parents=[db_parameters,
                                                                   date_parameters])
    status_workdays_parser.add_argument('-i', '--invoice_id', type=int,
                                        help='''Only show workdays associated with
                                        specified invoice id.''')
    status_workdays_parser.set_defaults(func=status, parser_object=status_workdays_parser.prog)

    # Export parser
    export_parser = main_subparsers.add_parser('export', aliases=['x'],
                                               help='Export hours to file.',
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
    delete_parser = main_subparsers.add_parser('delete', aliases=['d'],
                                          help='Delete a registered worktime.',
                                          parents=[db_parameters])
    delete_parser.add_argument('--id', type=str, default='current', help='''Choose
                               id to delete (or to delete tag under).
                               Default is to delete current stamp.''')
    delete_parser.add_argument('-t', '--tag', type=int, help='''Choose tag id to
                               delete.''')
    delete_parser.set_defaults(func=delete)

    # Edit parser
    edit_parser = main_subparsers.add_parser('edit', aliases=['e'],
                                             help='''Edit everything related to
                                             workdays or tags.''',
                                             parents=[db_parameters])
    edit_subparsers = edit_parser.add_subparsers()
    # Edit workday
    edit_workday_parser = edit_subparsers.add_parser('workday', aliases=['w', 'wd'],
                                                     help='Edit anything related to a workday.',
                                                     parents=[db_parameters])
    edit_workday_parser.add_argument('id', type=int, default='current', help='''
                                     Choose id of workday to edit.''')
    edit_workday_parser.add_argument('-d', '--date', type=str,
                                      help='Change from and to date.')
    edit_workday_parser.add_argument('-t', '--time', type=str,
                                      help='Change from and to time.')
    edit_workday_parser.add_argument('-c', '--comment', type=str,
                                      help='Change comment.')
    edit_workday_parser.add_argument('-u', '--customer', type=str,
                                      help='Change customer.')
    edit_workday_parser.set_defaults(func=edit, parser_object=edit_workday_parser.prog)
    edit_workday_subparsers = edit_workday_parser.add_subparsers()
    # Edit workday time
    edit_workday_time_parser = edit_workday_subparsers.add_parser('time', aliases=['t'],
                                                                  help='Edit the time registered on a workday.',
                                                                  parents=[db_parameters])
    edit_workday_time_parser.add_argument('-s', '--start', type=str,
                                          help='''Specify start time to store.''')
    edit_workday_time_parser.add_argument('-e', '--end', type=str,
                                          help='''Specify start time to store.''')
    # Edit workday tag
    edit_workday_tag_parser = edit_workday_subparsers.add_parser('tag', aliases=['tg'],
                                                                 help='Edit tags that are related to the workday.',
                                                                 parents=[db_parameters])
    # Edit customer
    edit_customer_parser = edit_subparsers.add_parser('customer', aliases=['c'],
                                                      help='Edit anything related to selected customer.',
                                                      parents=[db_parameters])
    edit_customer_parser.add_argument('id', type=int, default='current', help='''
                                      Choose id of customer to edit.''')
    edit_customer_parser.add_argument('-n', '--name', type=str,
                                      help='Change name.')
    edit_customer_parser.add_argument('-c', '--contact', type=str,
                                      help='Change contact person.')
    edit_customer_parser.add_argument('-o', '--org_nr', type=str,
                                      help='Change organization number.')
    edit_customer_parser.add_argument('-a', '--address', type=str,
                                      help='Change address.')
    edit_customer_parser.add_argument('-z', '--zip_code', type=str,
                                      help='Change zip code.')
    edit_customer_parser.add_argument('-m', '--mail', type=str,
                                      help='Change mail.')
    edit_customer_parser.add_argument('-p', '--phone', type=str,
                                      help='Change phone number.')
    edit_customer_parser.set_defaults(func=edit, parser_object=edit_customer_parser.prog)

    # Edit project
    edit_project_parser = edit_subparsers.add_parser('project', aliases=['p'],
                                                      help='Edit anything related to selected project.',
                                                      parents=[db_parameters])
    edit_project_parser.add_argument('id', type=int, default='current',
                                     help='Choose id of project to edit.')
    edit_project_parser.add_argument('-n', '--name', type=str,
                                      help='Change name.')
    edit_project_parser.add_argument('-u', '--link', type=str,
                                      help='Change link to website.')
    edit_project_parser.set_defaults(func=edit, parser_object=edit_project_parser.prog)

    return main_parser.parse_args(args)
