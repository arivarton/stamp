import sys

from datetime import datetime

from . import DB_SESSION
from .db import current_stamp
from .pprint import yes_or_no
from .helpers import auto_correct_tag, manually_correct_tag


def stamp_out(args):
    stamp = current_stamp()
    stamp.end = datetime.combine(args.date, args.time)
    for tag in stamp.tags:
        if tag.recorded > stamp.end or tag.recorded < stamp.start:
            print('Tag with id %d has a recorded date/time that is out of the stamp\'s bounds. Please correct the recorded tag date/time.' % tag.id_under_workday)
            yes_or_no('Do you wish for the tag to be auto corrected?',
                      no_message='Not auto correcting tags!',
                      no_function=yes_or_no,
                      no_function_args=('Do you wish to manually edit the tag?',),
                      no_function_kwargs={'no_message': 'Exiting...',
                                          'no_function': sys.exit,
                                          'no_function_args': (0,),
                                          'yes_function': manually_correct_tag,
                                          'yes_function_args': (tag, stamp,)},
                      yes_message='Auto correcting tags!',
                      yes_function=auto_correct_tag,
                      yes_function_args=(tag, stamp,))
    DB_SESSION.add(stamp)
    DB_SESSION.commit()
    print('Stamped out at %s - %s' % (args.date.isoformat(), args.time.isoformat()))
    return
