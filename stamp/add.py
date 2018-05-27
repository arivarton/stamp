import sys
from datetime import datetime

from .mappings import Workday
from .db import current_stamp
from . import DB_SESSION


def stamp_in(args):
    stamp = current_stamp()
    if stamp:
        user_choice = input('Already stamped in, do you wish to delete the current stamp [Y/n]? ')
        if user_choice.lower() in ['y', '']:
            DB_SESSION.delete(stamp)
            stamp = Workday(start=datetime.combine(args.date, args.time),
                            company=args.company)
            DB_SESSION.add(stamp)
            DB_SESSION.commit()
        else:
            print('Former stamp preserved.')

    print('Stamped in at %s - %s' % (stamp.start.date.isoformat(),
                                     stamp.start.time.isoformat()))
    return stamp
