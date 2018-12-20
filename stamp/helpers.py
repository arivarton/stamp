import sys
import shutil
from datetime import datetime, timedelta

__all__ = ['output_for_total_hours_date_and_wage',
           'auto_correct_tag',
           'manually_correct_tag',
           'get_terminal_width',
           'get_month_names',
           'error_handler']

def _determine_total_hours_worked_and_wage_earned(workdays, config):
    # If workdays is an object (Workday) it must be put in a list
    try:
        workdays = list(workdays)
    except TypeError:
        workdays = [workdays]

    total_time = timedelta()
    total_wage = 0

    for workday in workdays:
        if workday.end:
            total_seconds = (workday.end - workday.start).total_seconds()
            hours = total_seconds // 3600
            if hours < config.minimum_hours.value:
                hours = config.minimum_hours.value
                minutes = 0
            else:
                minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60 # NOQA

            # Add hours to wage
            total_wage += hours * config.wage_per_hour.value

            # Add minutes to wage
            # Minutes logic:
            # If worktime has not reached 15 minutes there will be no added wage.
            # If minutes is between 15 and 44.59 there will be half an hour added.
            # If minutes is 45+ there will be added an hour...
            if minutes >= 15 and minutes < 45:
                total_wage += config.wage_per_hour.value * 0.5
                minutes = 30
            elif minutes >= 45:
                total_wage += config.wage_per_hour.value * 1
                minutes = 60
            else:
                minutes = 0

            total_time += timedelta(hours=hours, minutes=minutes)
        else:
            pass

    return total_time.total_seconds() // 3600, (total_time.total_seconds() % 3600) // 60, total_wage


def output_for_total_hours_date_and_wage(workday, config):
    hours, minutes, wage = _determine_total_hours_worked_and_wage_earned(workday, config)
    output_total_wage = '%d%s' % (wage, config.currency.value)
    output_total_hours = '%dh' % hours
    if minutes:
        output_total_hours += ', %dm' % minutes
    # Add output date if the workday is not a list
    # If workday is a list, then it means total hours are being calculated
    # and the date is unneccesary
    try:
        output_date = workday.start.date().isoformat()
    except AttributeError:
        output_date = None
    return output_total_hours, output_date, output_total_wage


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
