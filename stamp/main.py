from .add import stamp_in
from .end import stamp_out
from .edit import edit_workday, edit_customer, edit_project
from .status import print_current_stamp, print_invoices, Status
from .delete import delete_workday_or_tag
from .tag import tag_stamp
from .db import Database
from .export import export_invoice
from .exceptions import (NoMatchingDatabaseEntryError, CurrentStampNotFoundError,
                         NoMatchesError, TooManyMatchesError, CanceledByUser)
from .helpers import error_handler


def add(args):
    try:
        stamp_in(args)
    except (CurrentStampNotFoundError, CanceledByUser) as err_msg:
        error_handler(err_msg, db=args.db)
    args.db.commit()

    return True


def end(args):
    try:
        stamp_out(args)
        args.db.commit()
    except (CurrentStampNotFoundError, CanceledByUser) as err_msg:
        error_handler(err_msg, db=args.db)

    return True


def tag(args):
    try:
        if args.id == 'current':
            stamp = args.db.current_stamp()
        else:
            stamp = args.db.query_for_workdays(workday_id=int(args.id))
    except (CurrentStampNotFoundError, CanceledByUser) as err_msg:
        error_handler(err_msg, db=args.db)

    tag_stamp(args.db, args.date, args.time, stamp, args.tag)
    args.db.commit()

    return True


def status(args):
    args.interface = 'cli'
    try:
        status_selection = args.parser_object.split(' ')[-1]
        if status_selection == 'invoices':
            print_invoices(args.db.get_invoices(args))
        elif status_selection == 'workdays':
            workdays = args.db.query_for_workdays(args=args)
            status_object = Status(workdays)
            if args.interface == 'cli':
                print(status_object)
            elif args.interface == 'ui':
                status_object.ui()
        else:
            try:
                print_current_stamp(args.db.current_stamp())
            except CurrentStampNotFoundError as err_msg:
                error_handler(err_msg, exit_on_error=False)
    except NoMatchingDatabaseEntryError as err_msg:
        error_handler(err_msg, exit_on_error=False)
    except CanceledByUser as err_msg:
        error_handler(err_msg, db=args.db)


    return True


def export(args):
    try:
        return export_invoice(args.db, args.year, args.month, args.customer,
                              args.project, args.pdf)
    except (NoMatchingDatabaseEntryError, TooManyMatchesError, NoMatchesError,
            CanceledByUser) as err_msg:
        error_handler(err_msg, db=args.db)
    args.db.session.commit()

    return True


def delete(args):
    if args.id == 'current':
        try:
            args.id = args.db.current_stamp().id
        except CurrentStampNotFoundError as err_msg:
            error_handler(err_msg, db=args.db, exit_on_error=False)
    else:
        args.id = int(args.id)
    delete_workday_or_tag(args.db, args.id, args.tag)
    args.db.commit()

    return True


# Edit only supports customer for now
def edit(args):
    edit_selection = args.parser_object.split(' ')[-1]
    if edit_selection == 'workday':
        if args.id == 'current':
            try:
                args.id = args.db.current_stamp().id
            except CurrentStampNotFoundError as err_msg:
                error_handler(err_msg, db=args.db)
        try:
            result = edit_workday(args.db)
        except NoMatchingDatabaseEntryError as err_msg:
            error_handler(err_msg, db=args.db)

    elif edit_selection == 'customer':
        try:
            result = edit_customer(args)
        except NoMatchingDatabaseEntryError as err_msg:
            error_handler(err_msg, db=args.db)

    elif edit_selection == 'project':
        try:
            result = edit_project(args)
        except NoMatchingDatabaseEntryError as err_msg:
            error_handler(err_msg, db=args.db)

    args.db.add(result)
    args.db.commit()

    return True
