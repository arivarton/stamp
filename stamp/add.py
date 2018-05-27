from datetime import datetime

from .mappings import Workday
from .db import current_stamp
from . import DB_SESSION


def _create_stamp(args, stamp):
    stamp.start = datetime.combine(args.date, args.time)
    DB_SESSION.add(stamp)
    DB_SESSION.commit()

    return stamp


def stamp_in(args):
    stamp = current_stamp()
    preserved_message = 'Former stamp preserved.'
    if stamp:
        try:
            user_choice = input('Already stamped in, do you wish to recreate the stamp with current date and time [Y/n]? ')
        except KeyboardInterrupt:
            user_choice = 'n'
            preserved_message = '\n' + preserved_message
        if user_choice.lower() in ['y', '']:
            stamp = _create_stamp(args, stamp)
        else:
            print(preserved_message)
    else:
        stamp = Workday(company=args.company)
        stamp = _create_stamp(args, stamp)

    print('Stamp: %s - %s' % (stamp.start.date().isoformat(),
                              stamp.start.time().isoformat()))
    return stamp
