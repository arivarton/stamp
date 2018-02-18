from datetime import datetime

from __init__ import DB_SESSION
from db import current_stamp


def stamp_out(args):
    stamp = current_stamp()
    stamp.end = datetime.combine(args.date, args.time)
    for tag in stamp.tags:
        if tag.recorded > stamp.end:
            raise Exception('''Tag with id %d has a recorded date/time that is
                            newer than the stamp\'s end date. Please correct the
                            recorded tag date/time.''' % tag.id_under_workday)
    DB_SESSION.add(stamp)
    DB_SESSION.commit()
    print('Stamped out at %s - %s' % (args.date.isoformat(), args.time.isoformat()))
    return
