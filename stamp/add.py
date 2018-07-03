import sys
from datetime import datetime

from .exceptions import NoMatchingDatabaseEntryError, CurrentStampNotFoundError
from .mappings import Workday, Project, Customer, Invoice
from .db import Database
from .formatting import yes_or_no, provide_input, value_for


def _create_stamp(Session, start_date, stamp):
    stamp.start = start_date
    Session.add(stamp)
    Session.commit()

    return stamp


def _add_details(Session, Table):
    for key, column_info in Table.__mapper__.columns.items():
        if not key.endswith('id'):
            if not getattr(Table, key):
                user_value = value_for(column_info.name.lower())
                setattr(Table, key, user_value)
    Session.add(Table)
    Session.commit()


def create_project(Session, customer_id, project_name=None):
    if not project_name:
        project_name = provide_input('project name')
    project = Project(name=project_name, customer_id=customer_id)
    yes_or_no('Do you wish to add project details?',
              no_message='Skipping project details!',
              yes_message='Adding project details. When entering a empty string the value will be set to None.',
              yes_function=_add_details,
              yes_function_args=(Session, project))

    Session.add(project)
    Session.commit()

    return project


def create_customer(Session, customer_name=None):
    if not customer_name:
        customer_name = provide_input('customer name')
    customer = Customer(name=customer_name)
    yes_or_no('Do you wish to add customer details?',
              no_message='Skipping customer details!',
              yes_message='Adding customer details. When entering a empty string the value will be set to None.',
              yes_function=_add_details,
              yes_function_args=(Session, customer))

    Session.add(customer)
    Session.commit()

    return customer


def create_invoice(db, workdays, customer, year, month):
    if isinstance(db, str):
        db = Database(db)

    customer = db.get_one_db_entry('Customer', 'name', customer)

    invoice = Invoice(workdays=workdays.all(),
                      customer_id=customer.id,
                      year=year,
                      month=month,
                      created=datetime.now())

    db.session.add(invoice)

    return invoice


def stamp_in(args):
    db = Database(args.db)
    try:
        stamp = db.current_stamp()
        stamp = yes_or_no('Already stamped in, do you wish to recreate the stamp with current date and time?',
                          no_message='Former stamp preserved!',
                          yes_message='Overwriting current stamp!',
                          yes_function=_create_stamp,
                          yes_function_args=(db.session,
                                             datetime.combine(args.date, args.time),
                                             stamp))
    except CurrentStampNotFoundError:
        try:
            if args.customer:
                customer_id = db.get_one_db_entry('Customer', 'name', args.customer).id
            else:
                customer_id = db.get_last_workday_entry('customer', 'id')
        except NoMatchingDatabaseEntryError:
            __ = yes_or_no('Do you wish to create a new customer?',
                           no_message='Canceling...',
                           no_function=sys.exit,
                           no_function_args=(0,),
                           yes_function=create_customer,
                           yes_function_args=(db.session, args.customer,))

            customer_id = __.id

        try:
            if args.project:
                project_id = db.get_one_db_entry('Project', 'name', args.project).id
            else:
                project_id = db.get_last_workday_entry('project', 'id')
        except NoMatchingDatabaseEntryError:
            __ = yes_or_no('Do you wish to create a new project?', # NOQA
                           no_message='Canceling...',
                           no_function=sys.exit,
                           no_function_args=(0,),
                           yes_function=create_project,
                           yes_function_args=(db.session, customer_id),
                           yes_function_kwargs={'project_name': args.project})

            project_id = __.id

        _workday = Workday(customer_id=customer_id, project_id=project_id)

        stamp = _create_stamp(db.session, # NOQA
                              datetime.combine(args.date, args.time), _workday)

    print('Stamped in at %s %s' % (stamp.start.time().strftime('%H:%M'),
                                   stamp.start.date().strftime('%x')))

    return stamp
