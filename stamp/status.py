from .db import current_stamp
from .helpers import output_for_total_hours_date_and_wage


def print_status(workdays):
    time_format = '%H:%M'

    # Headlines
    date_headline = 'Date'
    customer_headline = 'Customer'
    from_headline = 'From'
    to_headline = 'To'

    # Width for columns
    date_width = max(len(workdays.first().start.date().isoformat()), len(date_headline)) + 3
    customer_width = max(len(max([x.customer.name for x in workdays.all()], key=len)), len(customer_headline)) + 4
    from_width = max(len(workdays.first().start.strftime(time_format)), len(from_headline))
    to_width = max(len(workdays.first().end.strftime(time_format)), len(to_headline))
    id_width = len(max([str(x.id) for x in workdays.all()], key=len)) + 2

    # Header
    print('{0:<{id_width}} {1:<{date_width}} {2:<{customer_width}} {3:<{from_width}}   {4:<{to_width}}'.format(
        '',
        date_headline,
        customer_headline,
        from_headline,
        to_headline,
        date_width=date_width,
        customer_width=customer_width,
        from_width=from_width,
        to_width=to_width,
        id_width=id_width,
        ))

    # Output for each day
    for workday in workdays:
        output_total_hours, output_date, output_total_wage = output_for_total_hours_date_and_wage(workday)
        print('{0:<{id_width}} {1:<{date_width}} {2:<{customer_width}} {3:<{from_width}} - {4:<{to_width}} {5:_>30}'.format(
            workday.id,
            output_date,
            workday.customer.name,
            workday.start.strftime(time_format),
            workday.end.strftime(time_format),
            output_total_hours + ' for ' + output_total_wage,

            date_width=date_width,
            customer_width=customer_width,
            from_width=from_width,
            to_width=to_width,
            id_width=id_width,
        ))

    # Total
    output_total_hours, __, output_total_wage = output_for_total_hours_date_and_wage(workdays)
    print('\nTotal hours: %s' % output_total_hours)
    print('Total wage earned: %s' % output_total_wage)


def print_current_stamp():
    stamp = current_stamp()
    if stamp is not None:
        print('\n\nCurrent stamp:')
        print('%s %s' % (stamp.start.date().isoformat(), stamp.start.time().isoformat().split('.')[0]))
        print('Company: %s' % stamp.company)
        print('%d tag(s):' % len(stamp.tags.all()))
        for tag in stamp.tags:
            print('\t[id: %d] [Tagged: %s | %s]\n\t%s' % (tag.id_under_workday, tag.recorded.date().isoformat(), tag.recorded.time().isoformat(), tag.tag))
        print('')
    else:
        print('\nNot stamped in.')
