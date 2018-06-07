import sys

from sqlalchemy.orm import exc

from . import DB_SESSION
from .mappings import Workday, Tag, Customer
from .exceptions import NoMatchingDatabaseEntryError


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


def query_db_export_filter(Table, export_filter):
    table = eval(Table) # NOQA
    query = DB_SESSION.query(table)
    for key, value in export_filter.items():
        query = query.filter(value['op_func'](getattr(table, key), value['value']))
        if not query.count():
            raise NoMatchingDatabaseEntryError('No matching database entry found with search string: %s' % value['value'])

    return query


def query_db(Table, column_name, search_string):
    table = eval(Table) # NOQA
    db_filter = getattr(table, column_name)
    db_filter = db_filter.is_(search_string)

    return DB_SESSION.query(table).filter(db_filter)


def get_db_entries(Table, column_name, search_string):
    query = query_db(Table, column_name, search_string)

    if query.count():
        return query.all()
    else:
        raise NoMatchingDatabaseEntryError('No matching database entry found with search string: %s' % search_string)


def get_one_db_entry(Table, column_name, search_string):
    query = query_db(Table, column_name, search_string)

    if query.count() == 1:
        return query.first()
    elif query.count() > 1:
        print('Several database entries found matching', search_string + '!')
        print('Canceling...')
        sys.exit(0)
    else:
        # [TODO] Log that no matching database entries were found
        raise NoMatchingDatabaseEntryError('No matching database entry found with search string: %s' % search_string)


def get_last_workday_entry(*args):
    query = DB_SESSION.query(Workday).order_by(Workday.id).first()
    if not query:
        raise NoMatchingDatabaseEntryError('No matching database entry found with args: %s' % '.'.join(args))
    else:
        for attr in args:
            query = getattr(query, attr)
        return query
