import sys
from sqlalchemy.orm.query import Query
from .helpers import output_for_total_hours_date_and_wage, get_terminal_width
from .formatting import divider
from .exceptions import RequiredValueError


class Column(object):
    def __init__(self, name=None width=10, headline=''):
        if not name and headline is '':
            raise RequiredValueError('If no headline is set, name is required to be set!')
        if not name:
            self.name = headline
        else:
            self.name = name
        if not isinstance(width, int):
            raise ValueError('width argument must be an int!')
        self.width = width
        self.headline = headline
        if not isinstance(self.name, str) and isinstance(self.headline, str):
            raise ValueError('name and headline arguments must be str types!')


class ColumnWrapper(object):
    def add(self, column):
        if issubclass(column.__class__, Column):
            name = column.name.lower().replace(' ', '_')
            setattr(self, name, column)
        else:
            raise ValueError('column argument must be a Column class!')
    def total_width(self):
        total_width = 0
        for width in vars(self).values():
            total_width += width
        return total_width


class Table(object):
    def __init__(self):
        self.columns = ColumnWrapper()


class Status(object):
    def __init__(self, db_query):
        self.time_format = '%H:%M'
        if hasattr(db_query, '_primary_entity'):
            self.table = str(db_query._primary_entity.selectable)
        else:
            self.table = str(db_query.__table__)
        if issubclass(db_query.__class__, Query):
            self.db_query = db_query.all()
        else:
            self.db_query = [db_query]

    def __str__(self):
        if self.table == 'workday':
            return self.workdays()
        elif self.table == 'invoice':
            return self.invoices()

    def printable_workday(self):
        return_value = ''
        return_value += '\n' + self.id.get_headline() + self.date.get_headline() + self.customer.get_headline() + self.project.get_headline() + self.from_time.get_headline() + self.to_time.get_headline() + self.invoice_id.get_headline() + self.total_workday.get_headline() + '\n'
        return_value += divider()
        for workday_id, date, customer, project, from_time, to_time, invoice_id, total_workday, tags in zip(self.id, self.date, self.customer, self.project, self.from_time, self.to_time, self.invoice_id, self.total_workday, self.tags):
            return_value += '\n' + workday_id + date + customer + project + from_time + to_time + invoice_id + total_workday + '\n'
            return_value += divider()
            return_value += '\n' + 'the tag: ' + tags[1] + '\n'
            return_value += divider()
        return return_value

    def curses_friendly(self):
        return_value = []
        headline = self.id.get_headline() + self.date.get_headline() + self.customer.get_headline() + self.project.get_headline() + self.from_time.get_headline() + self.to_time.get_headline() + self.invoice_id.get_headline() + self.total_workday.get_headline()
        for workday_id in self.id:
            return_value += '\n' + workday_id + date + customer + project + from_time + to_time + invoice_id + total_workday + '\n'
            return_value += divider()
        return return_value


    def workdays(self):
        workdays = Table()
        workdays.columns.add(Column(name='id',
                             width=len(max([str(x.id) for x in self.db_query], key=len)) + 2))
        workdays.columns.add(Column(headline='Date',
                                    width=max(len(self.db_query[0].start.date().isoformat()), len(headlines['date'])) + 3))
        workdays.columns.add(Column(headline='Customer',
                                    width=max(len(max([x.customer.name for x in self.db_query], key=len)), len(headlines['customer'])) + 2))
        workdays.columns.add(Column(headline='Project',
                                    width=max(len(max([x.project.name for x in self.db_query], key=len)), len(headlines['project'])) + 4))
        workdays.columns.add(Column(headline='From',
                                    width=max(len(self.db_query[0].start.strftime(self.time_format)), len(headlines['from']))))
        workdays.columns.add(Column(headline='To',
                                    width=max(len(self.db_query[0].end.strftime(self.time_format)), len(headlines['to']))))
        workdays.columns.add(Column(headline='Invoice ID',
                                    width=max(len(max([str(x.invoice_id) for x in self.db_query], key=len)), len(headlines['invoice_id']))))

        # Headlines
        headlines = {
            'date': 'Date',
            'customer': 'Customer',
            'project': 'Project',
            'from': 'From',
            'to': 'To',
            'invoice_id': 'Invoice ID',
            'total_workday': 'Total'
        }

        # Width for columns
        total_widths = sum(widths.values())


        return_str = divider()
        return_str += '\n'
        # TODO:
        return_str += '{0:<{id_width}}{1:<{date_width}}{2:<{customer_width}}{3:<{project_width}}{4:<{from_width}}{5:<{to_width}}{6:^{invoice_id_width}}{7:>{total_width}}'.format(
                         workdays.columns.id.headline,
                         workdays.columns.date.headline,
                         workdays.columns.customer.headline,
                         workdays.columns.project.headline,
                         workdays.columns.from.headline,
                         workdays.columns.to.headline,
                         workdays.columns.invoice_id.headline,
                         workdays.columns.invoice_id.headline,
                         headlines['total_workday'],
                         id_width=widths['id'],
                         date_width=widths['date'],
                         customer_width=widths['customer'],
                         project_width=widths['project'],
                         from_width=widths['from'],
                         to_width=widths['to'],
                         invoice_id_width=widths['invoice_id'],
                         total_width=get_terminal_width() - (workdays.columns.total_width() + 5)
                         )
        return_str += '\n' + divider()

        # Output for each workday
        for workday in self.db_query:
            total_time, date, total_owed = output_for_total_hours_date_and_wage(workday)
            total_output = total_time + ' for ' + total_owed,
            total_width = get_terminal_width() - (sum(widths.values()) + len(total_output))
            return_str += '{0:<{id_width}}{1:<{date_width}}{2:<{customer_width}}{3:<{project_width}}{4:<{from_width}}{5:<{to_width}}{6:^{invoice_id_width}}{7:>{total_width}}'.format(
                            workday.id,
                            workday.start.date().isoformat(),
                            workday.customer.name,
                            workday.project.name,
                            workday.start.strftime(self.time_format),
                            workday.end.strftime(self.time_format),
                            workday.invoice_id or '',
                            total_time + ' for ' + total_owed,
                            id_width=widths['id'],
                            date_width=widths['date'],
                            customer_width=widths['customer'],
                            project_width=widths['project'],
                            from_width=widths['from'],
                            to_width=widths['to'],
                            invoice_id_width=widths['invoice_id'],
                            total_width=total_width
                        )
            return_str += '\n' + divider()

        return return_str


    def invoices(self):
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
            'id': len(max([str(x.id) for x in self.db_query], key=len)) + 2,
            'created': max(len(self.db_query[0].created.date().isoformat()), len(created_headline)) + 3,
            'customer': max(len(self.db_query[0].customer.name), len(customer_headline)) + 3,
            'year': max(len(max([x.year if x.year else '' for x in self.db_query], key=len)), len(year_headline)) + 1,
            'month': max(len(max([x.month if x.month else '' for x in self.db_query], key=len)), len(month_headline)) + 3,
            'pdf': max(len(max([x.pdf if x.pdf else '' for x in self.db_query], key=len)), len(pdf_headline), len(not_exported_message)) + 4,
            'sent': max(len('Yes'), len(sent_headline)) + 1,
            'paid': max(len('Yes'), len(paid_headline))
        }

        widths.update({'total': sum(widths.values()) + 7})

        return_str = divider()
        return_str += '\n'
        return_str += '{0:<{id_width}} {1:<{created_width}} {2:<{customer_width}} {3:<{year_width}} {4:<{month_width}} {5:<{pdf_width}} {6:<{sent_width}} {7:<{paid_width}}'.format(
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
                         )
        return_str += '\n' + divider()

        # Output for each invoice
        for invoice in self.db_query:

            if invoice.sent:
                invoice_sent = 'Yes'
            else:
                invoice_sent = 'No'

            if invoice.paid:
                invoice_paid = 'Yes'
            else:
                invoice_paid = 'No'

            return_str += '{0:<{id_width}} {1:<{created_width}} {2:<{customer_width}} {3:<{year_width}} {4:<{month_width}} {5:<{pdf_width}} {6:<{sent_width}} {7:<{paid_width}}'.format(
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
                        )
            return_str += '\n' + divider()

        return return_str


def print_current_stamp(current_stamp):
    result = '\nCurrent stamp:\n'
    result = result + '%s %s\n' % (current_stamp.start.date().isoformat(), current_stamp.start.time().isoformat().split('.')[0])
    result = result + 'Customer: %s\n' % current_stamp.customer.name
    result = result + '%d tag(s)' % len(current_stamp.tags.all())
    for tag in current_stamp.tags:
        result = result + '\n\t[id: %d] [Tagged: %s | %s]\n\t%s' % (tag.id, tag.recorded.date().isoformat(), tag.recorded.time().isoformat(), tag.tag)
    result = result + '\n'

    print(result)
