import sys

from sqlalchemy.orm import exc

from . import DB_SESSION
from .mappings import Workday, Tag, Customer


def query_for_workdays(workday_id=None, tag_id=None, args=None):
    try:
        # Used with delete or edit argument
        if workday_id or tag_id:
            if tag_id:
                workdays = DB_SESSION.query(Workday).get(workday_id).tags.filter(Tag.id_under_workday == tag_id)
            else:
                workdays = DB_SESSION.query(Workday).get(workday_id)

        # Used with status or export argument
        else:
            # Query with filter
            if hasattr(args, 'filter') and args.filter:
                if args.company:
                    workdays = DB_SESSION.query(Customer).filter(Customer.name is args.company).order_by(workdays.start)
                elif args.time and args.date:
                    print('Not implemented yet')
                elif args.date:
                    print('Not implemented yet')
                elif args.time:
                    print('Not implemented yet')
            # Query for everything (excludes current stamp)
            else:
                workdays = DB_SESSION.query(Workday).filter(Workday.end.isnot(None)).order_by(Workday.start)
    except exc.UnmappedInstanceError:
        print('Specified id not found')
    return workdays


def current_stamp():
    try:
        stamp = DB_SESSION.query(Workday).filter(Workday.end.is_(None))[0]
    except IndexError:
        stamp = None
    return stamp


def db_entry_exists(Table, column_name, search_string):
    _filter = getattr(Table, column_name)
    _filter = _filter.is_(search_string)
    _query = DB_SESSION.query(Table).filter(_filter)
    if _query.count() == 1:
        return _query.first().id
    elif _query.count() > 1:
        print('Several database entries found matching', search_string + '!')
        print('Canceling...')
        sys.exit(0)
    else:
        # [TODO] Log that no matching database entries were found
        return None
