from .helpers import output_for_total_hours_date_and_wage, get_terminal_width
from .pprint import divider


def print_status(workdays):
    time_format = '%H:%M'

    # Headlines
    date_headline = 'Date'
    customer_headline = 'Customer'
    from_headline = 'From'
    to_headline = 'To'

    # Width for columns
    widths = {
        'date': max(len(workdays.first().start.date().isoformat()), len(date_headline)) + 3,
        'customer': max(len(max([x.customer.name for x in workdays.all()], key=len)), len(customer_headline)) + 4,
        'from': max(len(workdays.first().start.strftime(time_format)), len(from_headline)),
        'to': max(len(workdays.first().end.strftime(time_format)), len(to_headline)),
        'id': len(max([str(x.id) for x in workdays.all()], key=len)) + 2
    }

    widths.update({'total': sum(widths.values()) + 6})

    # Header
    print('\n{0:<{id_width}} {1:<{date_width}} {2:<{customer_width}} {3:<{from_width}}   {4:<{to_width}}{5:>{summary_width}}'.format(
        '',
        date_headline,
        customer_headline,
        from_headline,
        to_headline,
        'Total',
        date_width=widths['date'],
        customer_width=widths['customer'],
        from_width=widths['from'],
        to_width=widths['to'],
        id_width=widths['id'],
        summary_width=get_terminal_width() - widths['total']
        ))

    divider()

    # Output for each day
    for workday in workdays:
        output_total_hours, output_date, output_total_wage = output_for_total_hours_date_and_wage(workday)
        print('{0:<{id_width}} {1:<{date_width}} {2:<{customer_width}} {3:<{from_width}} - {4:<{to_width}}{5:>{summary_width}}'.format(
            workday.id,
            output_date,
            workday.customer.name,
            workday.start.strftime(time_format),
            workday.end.strftime(time_format),
            output_total_hours + ' for ' + output_total_wage,

            date_width=widths['date'],
            customer_width=widths['customer'],
            from_width=widths['from'],
            to_width=widths['to'],
            id_width=widths['id'],
            summary_width=get_terminal_width() - widths['total']
        ))
        if workday.tags.count():
            for tag in workday.tags:
                print('{0:<{id_width}} {1}: {2}'.format(
                    tag.id,
                    tag.recorded.strftime(time_format),
                    tag.tag,
                    id_width=widths['id'],
                ))
        divider()

    # Total
    output_total_hours, __, output_total_wage = output_for_total_hours_date_and_wage(workdays)
    print('{0:>{summary_width}}'.format(
        output_total_hours + ' for ' + output_total_wage,

        summary_width=get_terminal_width()
    ))


def print_current_stamp(current_stamp):
    result = str()
    if current_stamp is not None:
        result = result + '\nCurrent stamp:\n'
        result = result + '%s %s\n' % (current_stamp.start.date().isoformat(), current_stamp.start.time().isoformat().split('.')[0])
        result = result + 'Customer: %s\n' % current_stamp.customer.name
        result = result + '%d tag(s)\n' % len(current_stamp.tags.all())
        for tag in current_stamp.tags:
            result = result + '\t[id: %d] [Tagged: %s | %s]\n\t%s' % (tag.id_under_workday, tag.recorded.date().isoformat(), tag.recorded.time().isoformat(), tag.tag)
        result = result + '\n'
    else:
        result = None

    return result
