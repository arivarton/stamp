from .add import stamp_in
from .end import stamp_out
from .edit import edit_regex_resolver, edit_workday
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
        db = Database(args.db)
        stamp_in(db, args)
    except (CurrentStampNotFoundError, CanceledByUser) as err_msg:
        error_handler(err_msg, db=db)
    db.commit()

    return True


def end(args):
    db = Database(args.db)
    try:
        stamp_out(db, args)
        db.commit()
    except (CurrentStampNotFoundError, CanceledByUser) as err_msg:
        error_handler(err_msg, db=db)

    return True


def tag(args):
    try:
        db = Database(args.db)
        if args.id == 'current':
            stamp = db.current_stamp()
        else:
            stamp = db.query_for_workdays(workday_id=int(args.id))
    except (CurrentStampNotFoundError, CanceledByUser) as err_msg:
        error_handler(err_msg, db=db)

    tag_stamp(db, args.date, args.time, stamp, args.tag)
    db.commit()

    return True


def status(args):
    args.interface = 'cli'
    try:
        db = Database(args.db)
        if args.invoices:
            print_invoices(db.get_invoices(args.show_superseeded))
        else:
            workdays = db.query_for_workdays(args=args)
            status_object = Status(workdays)
            if args.interface == 'cli':
                print(status_object)
            elif args.interface == 'ui':
                status_object.ui()
    except NoMatchingDatabaseEntryError as err_msg:
        error_handler(err_msg, exit_on_error=False)
    except CanceledByUser as err_msg:
        error_handler(err_msg)

    try:
        print_current_stamp(db.current_stamp())
    except CurrentStampNotFoundError as err_msg:
        error_handler(err_msg, exit_on_error=False)

    return True


def export(args):
    db = Database(args.db)
    try:
        return export_invoice(db, args.year, args.month, args.customer,
                              args.project, args.pdf)
    except (NoMatchingDatabaseEntryError, TooManyMatchesError, NoMatchesError,
            CanceledByUser) as err_msg:
        error_handler(err_msg, db=db)
    db.session.commit()

    return True


def delete(args):
    db = Database(args.db)
    if args.id == 'current':
        try:
            args.id = db.current_stamp().id
        except CurrentStampNotFoundError as err_msg:
            error_handler(err_msg, db=db, exit_on_error=False)
    else:
        args.id = int(args.id)
    delete_workday_or_tag(db, args.id, args.tag)
    db.commit()

    return True


# Edit only supports customer for now
def edit(args):
    db = Database(args.db)
    args.edit = edit_regex_resolver(args.edit)
    if args.id == 'current':
        try:
            args.id = db.current_stamp().id
        except CurrentStampNotFoundError as err_msg:
            error_handler(err_msg, db=db)
    else:
        try:
            args.id = int(args.id)
        except ValueError:
            error_handler('ID must be an integer!', db=db)
    edit_workday(db, args.id, args.edit)
    db.commit()

    return True
