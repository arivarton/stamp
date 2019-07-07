import sys
from datetime import datetime

from .exceptions import NoMatchingDatabaseEntryError, CurrentStampNotFoundError
from .mappings import Workday, Project, Customer, Invoice
from .db import Database
from .formatting import yes_or_no, provide_input, value_for
from .mappings import Customer, Project

__all__ = ['new_stamp',
           'create_invoice']

def create_stamp(db, customer, project, stamp, date, time):
    stamp.start = datetime.combine(date, time)
    stamp.customer = customer
    stamp.project = project
    db.add(stamp)

    return stamp


def add_details(Table):
    for key, column_info in Table.__mapper__.columns.items():
        if not key.endswith('id'):
            if not getattr(Table, key):
                user_value = value_for(column_info.name.lower(), ask=ask)
                setattr(Table, key, user_value)

    return Table


def create_project(db, customer_id, project_name=None, ask=True):
    if not project_name:
        project_name = provide_input('project name')
    project = Project(name=project_name, customer_id=customer_id)
    if ask:
        yes_or_no('Do you wish to add project details?',
                  no_message='Skipping project details!',
                  yes_message='Adding project details. When entering a empty string the value will be set to None.',
                  yes_function=add_details,
                  yes_function_args=(project,))

    db.add(project)

    return project


def create_customer(db, customer_name=None, ask=True):
    if not customer_name:
        customer_name = provide_input('customer name')
    customer = Customer(name=customer_name)
    if ask:
        yes_or_no('Do you wish to add customer details?',
                  no_message='Skipping customer details!',
                  yes_message='Adding customer details. When entering a empty string the value will be set to None.',
                  yes_function=add_details,
                  yes_function_args=(customer,))

    db.add(customer)

    return customer


def create_invoice(db, workdays, customer, year, month):
    if isinstance(db, str):
        db = Database(db)

    customer = db.get('Customer').filter(Customer.name == customer).first()

    invoice = Invoice(workdays=workdays.all(),
                      customer_id=customer.id,
                      year=year,
                      month=month,
                      created=datetime.now())

    db.add(invoice)

    return invoice


def new_stamp(db, customer, project, date, time, ask=True):
    try:
        if customer:
            customer_query = db.get('Customer').filter(Customer.name == customer).first()
        else:
            customer_query = db.get_last_workday_entry('customer')
    except NoMatchingDatabaseEntryError:
        if ask:
            customer_query = yes_or_no('Do you wish to create a new customer?',
                                       no_message='Canceling...',
                                       no_function=sys.exit,
                                       no_function_args=(0,),
                                       yes_function=create_customer,
                                       yes_function_args=(db, customer,))
        else:
            customer_query = create_customer(db, customer, ask=ask)

    # Validate project
    try:
        if project:
            project_query = db.get('Project').filter(Project.name == project).first()
        else:
            project_query = db.get_last_workday_entry('project')
    except NoMatchingDatabaseEntryError:
        if ask:
            project_query = yes_or_no('Do you wish to create a new project?', # NOQA
                                      no_message='Canceling...',
                                      no_function=sys.exit,
                                      no_function_args=(0,),
                                      yes_function=create_project,
                                      yes_function_args=(db, customer_query.id),
                                      yes_function_kwargs={'project_name': project})
        else:
            project_query = create_project(db, customer_query.id, project_name=project, ask=ask)

    # Create new stamp
    try:
        stamp = db.current_stamp()
        if ask:
            yes_or_no('Already stamped in, do you wish to recreate the stamp with current date and time?',
                      no_message='Former stamp preserved!',
                      yes_message='Overwriting current stamp!',
                      yes_function=create_stamp,
                      yes_function_args=(db, customer_query, project_query,
                                         stamp, date, time))
        else:
            create_stamp(db, customer_query, project_query, stamp, date, time)

    except CurrentStampNotFoundError:
        _workday = Workday(customer_id=customer_query.id, project_id=project_query.id)

        stamp = create_stamp(db, customer_query, project_query, _workday, date, time)

    print('Stamped in at %s %s' % (stamp.start.time().strftime('%H:%M'),
                                   stamp.start.date().strftime('%x')))
    return stamp
