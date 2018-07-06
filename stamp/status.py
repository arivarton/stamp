from .helpers import output_for_total_hours_date_and_wage, get_terminal_width
from .formatting import divider


def print_status(workdays):
    if not isinstance(workdays, list):
        workdays = workdays.all()
    time_format = '%H:%M'

    # Headlines
    date_headline = 'Date'
    customer_headline = 'Customer'
    project_headline = 'Project'
    from_headline = 'From'
    to_headline = 'To'
    invoice_id_headline = 'Invoice ID'

    # Width for columns
    widths = {
        'date': max(len(workdays[0].start.date().isoformat()), len(date_headline)) + 3,
        'customer': max(len(max([x.customer.name for x in workdays], key=len)), len(customer_headline)) + 2,
        'project': max(len(max([x.project.name for x in workdays], key=len)), len(project_headline)) + 4,
        'from': max(len(workdays[0].start.strftime(time_format)), len(from_headline)),
        'to': max(len(workdays[0].end.strftime(time_format)), len(to_headline)),
        'id': len(max([str(x.id) for x in workdays], key=len)) + 2,
        'invoice id': max(len(max([str(x.invoice_id) for x in workdays], key=len)), len(invoice_id_headline))
    }

    widths.update({'total': sum(widths.values()) + 11})

    # Header
    divider()
    print('{0:<{id_width}} {1:<{date_width}} {2:<{customer_width}} {3:<{project_width}} {4:<{from_width}}   {5:<{to_width}}   {6:^{invoice_id_width}}{7:>{summary_width}}'.format(
        '',
        date_headline,
        customer_headline,
        project_headline,
        from_headline,
        to_headline,
        invoice_id_headline,
        'Total',
        date_width=widths['date'],
        customer_width=widths['customer'],
        project_width=widths['project'],
        from_width=widths['from'],
        to_width=widths['to'],
        invoice_id_width=widths['invoice id'],
        id_width=widths['id'],
        summary_width=get_terminal_width() - widths['total']
        ))
    divider()

    # Output for each day
    for workday in workdays:
        output_total_hours, output_date, output_total_wage = output_for_total_hours_date_and_wage(workday)
        print('{0:<{id_width}} {1:<{date_width}} {2:<{customer_width}} {3:<{project_width}} {4:<{from_width}} - {5:<{to_width}}   {6:^{invoice_id_width}}{7:>{summary_width}}'.format(
            workday.id,
            output_date,
            workday.customer.name,
            workday.project.name,
            workday.start.strftime(time_format),
            workday.end.strftime(time_format),
            workday.invoice_id or '',
            output_total_hours + ' for ' + output_total_wage,

            date_width=widths['date'],
            customer_width=widths['customer'],
            project_width=widths['project'],
            from_width=widths['from'],
            to_width=widths['to'],
            invoice_id_width=widths['invoice id'],
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


def print_invoices(invoices):
    # Headlines
    created_headline = 'Created on'
    year_headline = 'Year'
    month_headline = 'Month'
    customer_headline = 'Customer'
    pdf_headline = 'PDF'
    sent_headline = 'Sent'
    paid_headline = 'Paid'
    not_exported_message = 'Not exported'

    # Width for columns
    widths = {
        'id': len(max([str(x.id) for x in invoices.all()], key=len)) + 2,
        'created': max(len(invoices.all()[0].created.date().isoformat()), len(created_headline)) + 3,
        'customer': max(len(invoices.all()[0].customer.name), len(customer_headline)) + 3,
        'year': max(len(max([x.year if x.year else '' for x in invoices.all()], key=len)), len(year_headline)) + 1,
        'month': max(len(max([x.month if x.month else '' for x in invoices.all()], key=len)), len(month_headline)) + 3,
        'pdf': max(len(max([x.pdf if x.pdf else '' for x in invoices.all()], key=len)), len(pdf_headline), len(not_exported_message)) + 4,
        'sent': max(len('Yes'), len(sent_headline)) + 1,
        'paid': max(len('Yes'), len(paid_headline))
    }

    widths.update({'total': sum(widths.values()) + 7})

    divider()
    print('{0:<{id_width}} {1:<{created_width}} {2:<{customer_width}} {3:<{year_width}} {4:<{month_width}} {5:<{pdf_width}} {6:<{sent_width}} {7:<{paid_width}}'.format(
        '',
        created_headline,
        customer_headline,
        year_headline,
        month_headline,
        pdf_headline,
        sent_headline,
        paid_headline,
        id_width=widths['id'],
        created_width=widths['created'],
        customer_width=widths['customer'],
        year_width=widths['year'],
        month_width=widths['month'],
        pdf_width=widths['pdf'],
        sent_width=widths['sent'],
        paid_width=widths['paid']
        ))
    divider()

    # Output for each invoice
    for invoice in invoices.all():

        if invoice.sent:
            invoice_sent = 'Yes'
        else:
            invoice_sent = 'No'

        if invoice.paid:
            invoice_paid = 'Yes'
        else:
            invoice_paid = 'No'

        print('{0:<{id_width}} {1:<{created_width}} {2:<{customer_width}} {3:<{year_width}} {4:<{month_width}} {5:<{pdf_width}} {6:<{sent_width}} {7:<{paid_width}}'.format(
            invoice.id,
            invoice.created.date().isoformat(),
            invoice.customer.name,
            invoice.year,
            invoice.month,
            invoice.pdf or not_exported_message,
            invoice_sent,
            invoice_paid,
            id_width=widths['id'],
            created_width=widths['created'],
            customer_width=widths['customer'],
            year_width=widths['year'],
            month_width=widths['month'],
            pdf_width=widths['pdf'],
            sent_width=widths['sent'],
            paid_width=widths['paid']
        ))
        divider()


def print_current_stamp(current_stamp):
    result = str()
    if current_stamp is not None:
        result = result + '\nCurrent stamp:\n'
        result = result + '%s %s\n' % (current_stamp.start.date().isoformat(), current_stamp.start.time().isoformat().split('.')[0])
        result = result + 'Customer: %s\n' % current_stamp.customer.name
        result = result + '%d tag(s)' % len(current_stamp.tags.all())
        for tag in current_stamp.tags:
            result = result + '\n\t[id: %d] [Tagged: %s | %s]\n\t%s' % (tag.id, tag.recorded.date().isoformat(), tag.recorded.time().isoformat(), tag.tag)
        result = result + '\n'
    else:
        result = None

    return result
