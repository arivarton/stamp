import sys
from datetime import datetime

from .exceptions import NoMatchingDatabaseEntryError
from .mappings import Workday, Project, Customer
from .db import current_stamp, db_entry_exists, get_last_workday_entry
from .pprint import yes_or_no
from . import DB_SESSION


def _create_stamp(args, stamp):
    stamp.start = datetime.combine(args.date, args.time)
    DB_SESSION.add(stamp)
    DB_SESSION.commit()

    return stamp


def _add_details(Table):
    for key, column_info in Table.__mapper__.columns.items():
        if not key.endswith('id'):
            if not getattr(Table, key):
                user_value = input('Value for ' + column_info.name.lower() + ': ')
                setattr(Table, key, user_value)
    DB_SESSION.add(Table)
    DB_SESSION.commit()


def create_project(customer_id, project_name=None):
    if not project_name:
        project_name = input('Provide project name: ')
        if not project_name:
            print('No project name provided!')
            print('Canceling...')
            sys.exit(0)
    project = Project(name=project_name, customer_id=customer_id)
    yes_or_no('Do you wish to add project details?',
              no_message='Skipping project details!',
              yes_message='Adding project details. When entering a empty string the value will be set to None.',
              yes_function=_add_details,
              yes_function_args=(project,))
    DB_SESSION.add(project)
    DB_SESSION.commit()

    return project


def create_customer(customer_name=None):
    if not customer_name:
        customer_name = input('Provide customer name: ')
        if not customer_name:
            print('No customer name provided!')
            print('Canceling...')
            sys.exit(0)
    customer = Customer(name=customer_name)
    yes_or_no('Do you wish to add customer details?',
              no_message='Skipping customer details!',
              yes_message='Adding customer details. When entering a empty string the value will be set to None.',
              yes_function=_add_details,
              yes_function_args=(customer,))
    DB_SESSION.add(customer)
    DB_SESSION.commit()

    return customer


def stamp_in(args):
    stamp = current_stamp()
    if stamp:
        stamp = yes_or_no('Already stamped in, do you wish to recreate the stamp with current date and time?',
                          no_message='Former stamp preserved!',
                          yes_message='Overwriting current stamp!',
                          yes_function=_create_stamp,
                          yes_function_args=(args, stamp))
    else:
        try:
            if args.company:
                customer_id = db_entry_exists(Customer, 'name', args.company)
            else:
                customer_id = get_last_workday_entry('customer', 'id')
        except NoMatchingDatabaseEntryError:
            __ = yes_or_no('Do you wish to create a new customer?',
                           no_message='Canceling...',
                           no_function=sys.exit,
                           no_function_args=(0,),
                           yes_message='Creating database entry!',
                           yes_function=create_customer,
                           yes_function_args=(args.company,))
            customer_id = __.id

        _workday = Workday(customer_id=customer_id)

        try:
            if args.project:
                project_id = db_entry_exists(Project, 'name', args.project)
            else:
                project_id = get_last_workday_entry('project', 'id')
        except NoMatchingDatabaseEntryError:
            __ = yes_or_no('Do you wish to create a new project?', # NOQA
                           no_message='Canceling...',
                           no_function=sys.exit,
                           no_function_args=(0,),
                           yes_message='Creating database entry!',
                           yes_function=create_project,
                           yes_function_args=(customer_id,),
                           yes_function_kwargs={'project_name': args.project})
            project_id = __.id

        _workday.project_id = project_id

        stamp = _create_stamp(args, _workday)

    print('Stamped in at %s - %s' % (stamp.start.date().isoformat(),
                                     stamp.start.time().isoformat()))

    return stamp
