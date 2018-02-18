from datetime import datetime

from __init__ import DB_SESSION
from mappings import Workday


def stamp_in(args):
    stamp = Workday(start=datetime.combine(args.date, args.time),
                    company=args.company)
    DB_SESSION.add(stamp)
    DB_SESSION.commit()
    print('Stamped in at %s - %s' % (args.date.isoformat(), args.time.isoformat()))
    return stamp
