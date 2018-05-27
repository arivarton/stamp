from datetime import datetime

from . import DB_SESSION
from .db import current_stamp
from .pprint import yes_or_no
from .helpers import auto_correct_tag


def stamp_out(args):
    stamp = current_stamp()
    stamp.end = datetime.combine(args.date, args.time)
    for tag in stamp.tags:
        if tag.recorded > stamp.end or tag.recorded < stamp.start:
            print('Tag with id %d has a recorded date/time that is out of the stamp\'s bounds. Please correct the recorded tag date/time.' % tag.id_under_workday)
            yes_or_no('Do you wish for the tag to be auto corrected?',
                      no_message='Not auto correcting tags! Please manually input the time and/or date.',
                      yes_message='Auto correcting tags!',
                      yes_function=auto_correct_tag,
                      yes_function_args=(tag,))
    DB_SESSION.add(stamp)
    DB_SESSION.commit()
    print('Stamped out at %s - %s' % (args.date.isoformat(), args.time.isoformat()))
    return
