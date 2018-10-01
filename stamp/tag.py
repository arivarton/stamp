from datetime import datetime

from .mappings import Tag
from .exceptions import TagOutsideTimeBoundaryError


def tag_stamp(db, date, time, stamp, tag):
    if stamp.end:
        if date > stamp.end.date():
            raise TagOutsideTimeBoundaryError('Tag (%s %s) must be set before the work day has ended (%s %s).' % (date, time, stamp.end.date(), stamp.end.time()))
        elif date == stamp.end.date() and time > stamp.end.time():
            raise TagOutsideTimeBoundaryError('Tag (%s %s) must be set before the work day has ended (%s %s).' % (date, time, stamp.end.date(), stamp.end.time()))
    if date < stamp.start.date():
        raise TagOutsideTimeBoundaryError('Tag (%s) must be set after the work day has started (%s).' % (date, stamp.start.date()))
    elif date == stamp.start.date() and time < stamp.start.time():
        raise TagOutsideTimeBoundaryError('Tag (%s) must be set after the work day has started (%s).' % (date, stamp.start.date()))
    else:
        tag = Tag(recorded=datetime.combine(date, time),
                              tag=tag)
        stamp.tags.append(tag)
        db.add(stamp)

        return tag
