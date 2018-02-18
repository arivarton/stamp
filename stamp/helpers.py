import math

from __init__ import MINIMUM_HOURS, WAGE_PER_HOUR, CURRENCY


def determine_total_hours_worked_and_wage_earned(workdays):
    # If workdays is an object (Workday) it must be put in a list
    try:
        workdays = list(workdays)
    except TypeError:
        workdays = [workdays]
    total_days = 0
    total_hours = 0
    total_minutes = 0
    total_wage = 0
    for workday in workdays:
        total = workday.end - workday.start
        hours = total.seconds / 3600
        total_days += total.days
        # Rounds up hours
        if round(hours) == math.ceil(hours):
            minutes = 0
        else:
            minutes = 30
        # If total work time is under MINIMUM_HOURS then set work time to
        # MINIMUM_HOURS instead
        if total.days is 0 and hours < MINIMUM_HOURS:
            hours = MINIMUM_HOURS
            total_hours += hours
            minutes = 0
        else:
            hours = round(hours)
            total_hours += hours
        # Increment hour if minutes has passed 60
        if minutes is 30 and total_minutes is 30:
            total_hours += 1
            total_minutes = 0
        total_minutes = minutes
        # Increment days if total hours has passed 23
        if total_hours >= 24:
            total_days += 1
            total_hours -= 24
    # Add to wage
    total_wage = ((total_days*24) * WAGE_PER_HOUR) + (total_hours * WAGE_PER_HOUR)
    if minutes is 30:
        total_wage += WAGE_PER_HOUR * 0.5
    return total_days, total_hours, total_minutes, total_wage


def output_for_total_hours_date_and_wage(workday):
    days, hours, minutes, wage = determine_total_hours_worked_and_wage_earned(workday)
    output_total_wage = '%d%s' % (wage, CURRENCY)
    if days:
        output_total_hours = '%dd' % days
        if hours:
            output_total_hours += ', %dh' % hours
    else:
        output_total_hours = '%dh' % hours
    if minutes:
        output_total_hours += ', %dm' % minutes
    # Add output date if the workday is not a list
    # If workday is a list, then it means total hours are being calculated
    # and the date is unneccesary
    try:
        if workday.start.date() == workday.end.date():
            output_date = workday.start.date().isoformat()
        else:
            output_date = '%s-%s' % (workday.start.date().isoformat(),
                                     workday.end.date().isoformat())
    except AttributeError:
        output_date = None
    return output_total_hours, output_date, output_total_wage
