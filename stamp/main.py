import sys

from .add import stamp_in
from .end import stamp_out
from .edit import edit_workday, edit_customer, edit_project, edit_invoice
from .status import print_current_stamp, Status
from .delete import delete_workday_or_tag
from .tag import tag_stamp
from .db import Database
from .export import export_invoice
from .exceptions import (NoMatchingDatabaseEntryError, CurrentStampNotFoundError,
                         NoMatchesError, TooManyMatchesError, CanceledByUser)
from .helpers import error_handler
from .decorators import db_commit_decorator, no_db_no_action_decorator

@db_commit_decorator
def add(args):
    try:
        return stamp_in(args)
    except (CurrentStampNotFoundError, CanceledByUser) as err_msg:
        error_handler(err_msg, db=args.db)


@no_db_no_action_decorator
@db_commit_decorator
def end(args):
    try:
        return stamp_out(args)
    except (CurrentStampNotFoundError, CanceledByUser) as err_msg:
        error_handler(err_msg, db=args.db)


@no_db_no_action_decorator
@db_commit_decorator
def tag(args):
    try:
        try:
            if args.id:
                stamp = args.db.query_for_workdays(workday_id=int(args.id))
            else:
                stamp = args.db.current_stamp()
        except CurrentStampNotFoundError as err_msg:
            error_handler(err_msg, db=args.db)
        return tag_stamp(args.db, args.date, args.time, stamp, args.tag)
    except CanceledByUser as err_msg:
        error_handler(err_msg, db=args.db)


@no_db_no_action_decorator
def status(args):
    args.interface = 'cli'
    try:
        if hasattr(args, 'db_query'):
            status_object = Status(args.db_query)
            if args.interface == 'cli':
                print(status_object)
            elif args.interface == 'ui':
                status_object.ui()
        else:
            try:
                print_current_stamp(args.db.current_stamp())
            except CurrentStampNotFoundError as err_msg:
                error_handler(err_msg)
    except NoMatchingDatabaseEntryError as err_msg:
        error_handler(err_msg, exit_on_error=False)
    except CanceledByUser as err_msg:
        error_handler(err_msg, db=args.db)


    return True

@no_db_no_action_decorator
@db_commit_decorator
def export(args):
    try:
        return export_invoice(args.db, args.year, args.month, args.customer,
                              args.project, args.pdf)
    except (NoMatchingDatabaseEntryError, TooManyMatchesError, NoMatchesError,
            CanceledByUser) as err_msg:
        error_handler(err_msg, db=args.db)


@no_db_no_action_decorator
@db_commit_decorator
def delete(args):
    try:
        if args.id:
            args.id = int(args.id)
        else:
                args.id = args.db.current_stamp().id
        delete_workday_or_tag(args.db, args)
    except (CurrentStampNotFoundError, NoMatchingDatabaseEntryError) as err_msg:
        error_handler(err_msg, db=args.db)


# Edit only supports customer for now
@no_db_no_action_decorator
@db_commit_decorator
def edit(args):
    edit_selection = args.parser_object.split(' ')[-1]
    try:
        if edit_selection == 'workday':
            if not args.id:
                try:
                    args.id = args.db.current_stamp().id
                except CurrentStampNotFoundError as err_msg:
                    error_handler(err_msg, db=args.db)
            changed_object = edit_workday(args)

        elif edit_selection == 'customer':
            changed_object = edit_customer(args)

        elif edit_selection == 'project':
            changed_object = edit_project(args)

        elif edit_selection == 'invoice':
            changed_object = edit_invoice(args)

    except NoMatchingDatabaseEntryError as err_msg:
        error_handler(err_msg, db=args.db)

    current_db_session = args.db.session.object_session(changed_object)
    current_db_session.add(changed_object)
    current_db_session.commit()
