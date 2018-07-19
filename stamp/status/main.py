from sqlalchemy.orm.query import Query

from ..formatting import divider
from .formatting.workday import Workday


class Status(object):
    def __init__(self, *args):
        self.delivered_objects = list()
        for attribute_object in args:
            if issubclass(attribute_object.__class__, Query):
                self.delivered_objects = attribute_object.all()
            else:
                raise AttributeError('''All args must be a sqlalchemy Query object.''')
        self.parsed_objects = list()
        for _object in self.delivered_objects:
            self.parsed_objects.append(Workday(_object))

    def __str__(self):
        return_value = ''
        for workday in self.parsed_objects:
            return_value += '\n' + workday.id + workday.date + workday.customer\
                + workday.project + workday.from_time + workday.to_time\
                + workday.invoice_id + workday.total_workday + '\n'
            return_value += divider()
        return return_value


            #  if self.tags.values[index]:
            #      for tag_id, recorded, message in self.tags.values:
            #          print('{0:<{id_width}} {1}: {2}'.format(
            #              tag_id,
            #              recorded,
            #              message,
            #              id_width=self.tags.width,
            #          ))

        # Total
        #  print('{0:>{summary_width}}'.format(
        #      self.total_hours + ' for ' + self.total_wage,

        #      summary_width=get_terminal_width()
        #  ))


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
