import sys
import shutil
from datetime import datetime, timedelta

__all__ = ['auto_correct_tag',
           'manually_correct_tag',
           'get_terminal_width',
           'get_month_names',
           'error_handler',
           'calculate_workhours',
           'calculate_wage']


def calculate_workhours(start, end):
    return (end - start).total_seconds()/60/60


def calculate_wage(hours, hourly_wage):
    return hours * hourly_wage


def auto_correct_tag(tag, stamp, Session):
    if tag.recorded < stamp.start:
        tag.recorded = stamp.start
    elif stamp.end:
        if tag.recorded > stamp.end:
            tag.recorded = stamp.end
    Session.add(tag)

    return True


def manually_correct_tag(tag, stamp, Session):
    print('\nTag is recorded at: %s.' % tag.recorded.strftime('%Y-%m-%d %H:%M'))
    print('Boundary is from %s to %s.\n' % (stamp.start.strftime('%Y-%m-%d %H:%M'), stamp.end.strftime('%Y-%m-%d %H:%M')))
    while tag.recorded < stamp.start or tag.recorded > stamp.end:
        try:
            manual_time = datetime.strptime(input('Please input the new time and date for tag in this format YYYY-mm-dd HH:MM: '), '%Y-%m-%d %H:%M')
            tag.recorded = manual_time
        except KeyboardInterrupt:
            print('Exiting...')
            sys.exit(0)
        except ValueError:
            manual_time = None
            print('Wrong format. Use this format: YYYY-mm-dd HH:MM')
        if manual_time:
            if manual_time < stamp.start or manual_time > stamp.end:
                print('New time is still out of bounds... Try again!')
            else:
                Session.add(tag)
                return True


def get_terminal_width():
    return shutil.get_terminal_size((80, 80)).columns


def get_month_names():
    return ['January', 'February', 'March', 'April', 'May', 'June', 'July',
            'August', 'September', 'October', 'November', 'December']


def error_handler(error_message, db=False, exit_on_error=True):
    print(error_message)
    if db:
        db.reset()
    if exit_on_error:
        sys.exit(0)
