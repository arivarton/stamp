import sys

from datetime import datetime

from .db import Database
from .pprint import yes_or_no
from .helpers import auto_correct_tag, manually_correct_tag
from .exceptions import CurrentStampNotFoundError


def stamp_out(args):
    db = Database(args.db)
    stamp = db.current_stamp()
    if not stamp:
        raise CurrentStampNotFoundError('No stamp present. Stamp in first!')
    stamp.end = datetime.combine(args.date, args.time)
    for tag in stamp.tags:
        if tag.recorded > stamp.end or tag.recorded < stamp.start:
            print('Tag with id %d has a recorded date/time that is out of the stamp\'s bounds. Please correct the recorded tag date/time.' % tag.id)
            yes_or_no('Do you wish for the tag to be auto corrected?',
                      no_message='Not auto correcting tags!',
                      no_function=yes_or_no,
                      no_function_args=('Do you wish to manually edit the tag?',),
                      no_function_kwargs={'no_message': 'Canceling...',
                                          'no_function': sys.exit,
                                          'no_function_args': (0,),
                                          'yes_function': manually_correct_tag,
                                          'yes_function_args': (tag, stamp,
                                                                db.session)},
                      yes_message='Auto correcting tags!',
                      yes_function=auto_correct_tag,
                      yes_function_args=(tag, stamp, db.session,))
    db.session.add(stamp)
    db.session.commit()
    print('Stamped out at %s %s' % (args.time.strftime('%H:%M'), args.date.strftime('%x')))
    return
