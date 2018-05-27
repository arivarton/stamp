from datetime import datetime

from .mappings import Workday
from .db import current_stamp
from .pprint import yes_or_no
from . import DB_SESSION


def _create_stamp(args, stamp):
    stamp.start = datetime.combine(args.date, args.time)
    DB_SESSION.add(stamp)
    DB_SESSION.commit()

    return stamp


def stamp_in(args):
    stamp = current_stamp()
    if stamp:
        stamp = yes_or_no('Already stamped in, do you wish to recreate the stamp with current date and time?',
                          no_message='Former stamp preserved!',
                          yes_message='Overwriting current stamp!',
                          yes_function=_create_stamp,
                          yes_function_args=(args, stamp))
    else:
        stamp = _create_stamp(args, Workday(company=args.company))

    print('Stamped in at %s - %s' % (stamp.start.date().isoformat(),
                                     stamp.start.time().isoformat()))

    return stamp
