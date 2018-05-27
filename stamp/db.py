from sqlalchemy.orm import exc

from . import DB_SESSION
from .mappings import Workday, Tag


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
            if args.filter:
                if args.company:
                    workdays = DB_SESSION.query(Workday).filter(Workday.company is args.company).order_by(Workday.start)
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
