import sys

from datetime import datetime

from .formatting import yes_or_no
from .helpers import auto_correct_tag, manually_correct_tag
from .exceptions import CurrentStampNotFoundError

__all__ = ['end_stamp']

def end_stamp(db, date, time):
    stamp = db.current_stamp()
    if not stamp:
        raise CurrentStampNotFoundError('No stamp present. Stamp in first!')
    stamp.end = datetime.combine(date, time)
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
    db.add(stamp)
    print('Stamped out at %s %s' % (time.strftime('%H:%M'), date.strftime('%x')))

    return stamp
