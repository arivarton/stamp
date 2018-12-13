import sys
from sqlalchemy.orm.query import Query
from .helpers import output_for_total_hours_date_and_wage, get_terminal_width
from .formatting import divider, boolean_yes_or_no
from .exceptions import RequiredValueError


class Column(object):
    def __init__(self, name=None, width=10, headline='', in_total_width=True):
        self.width = max(width, len(headline))
        self.headline = headline
        self.in_total_width = in_total_width
        if not name and headline is '':
            raise RequiredValueError('If no headline is set, name is required to be set!')
        if not name:
            self.name = headline
        else:
            self.name = name
        if not isinstance(width, int):
            raise ValueError('width argument must be an int!')
        if not isinstance(self.name, str) and isinstance(self.headline, str):
            raise ValueError('name and headline arguments must be str types!')


class ColumnWrapper(object):
    def add(self, column):
        if issubclass(column.__class__, Column):
            name = column.name.lower().replace(' ', '_')
            setattr(self, name, column)
        else:
            raise ValueError('column argument must be a Column class!')


class Table(object):
    def __init__(self):
        self.columns = ColumnWrapper()
    def total_column_width(self):
        total_width = 0
        for column in vars(self.columns).values():
            if column.in_total_width:
                total_width += column.width
        return total_width


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
                             width=len(max([str(x.id) for x in self.db_query], key=len)) + 3))
        workdays.columns.add(Column(headline='Date',
                                    width=len(self.db_query[0].start.date().isoformat()) + 3))
        workdays.columns.add(Column(headline='Customer',
                                    width=len(max([x.customer.name for x in self.db_query], key=len)) + 6))
        workdays.columns.add(Column(headline='Project',
                                    width=len(max([x.project.name for x in self.db_query], key=len)) + 6))
        workdays.columns.add(Column(name='from_date',
                                    headline='From',
                                    width=len(self.db_query[0].start.strftime(self.time_format)) + 3))
        workdays.columns.add(Column(name='to_date',
                                    headline='To',
                                    width=len(self.db_query[0].end.strftime(self.time_format)) + 3))
        workdays.columns.add(Column(headline='Invoice ID',
                                    width=len(max([str(x.invoice_id) for x in self.db_query], key=len))))
        workdays.columns.add(Column(headline='Total',
                                    width=0,
                                    in_total_width=False))
                                    

        return_str = divider()
        return_str += '\n'
        # TODO:
        return_str += '{0:<{id_width}}{1:^{date_width}}{2:^{customer_width}}{3:^{project_width}}{4:^{from_width}}{5:^{to_width}}{6:^{invoice_id_width}}{7:>{total_width}}'.format(
                         # Headlines
                         workdays.columns.id.headline,
                         workdays.columns.date.headline,
                         workdays.columns.customer.headline,
                         workdays.columns.project.headline,
                         workdays.columns.from_date.headline,
                         workdays.columns.to_date.headline,
                         workdays.columns.invoice_id.headline,
                         workdays.columns.total.headline,

                         # Widths
                         id_width=workdays.columns.id.width,
                         date_width=workdays.columns.date.width,
                         customer_width=workdays.columns.customer.width,
                         project_width=workdays.columns.project.width,
                         from_width=workdays.columns.from_date.width,
                         to_width=workdays.columns.to_date.width,
                         invoice_id_width=workdays.columns.invoice_id.width,
                         total_width=get_terminal_width() - (workdays.total_column_width())
                         )
        return_str += '\n' + divider()

        # Output for each workday
        for workday in self.db_query:
            total_time, date, total_owed = output_for_total_hours_date_and_wage(workday)
            total_output = total_time + ' for ' + total_owed
            total_width = get_terminal_width() - (workdays.total_column_width())
            return_str += '{0:<{id_width}}{1:^{date_width}}{2:^{customer_width}}{3:^{project_width}}{4:^{from_width}}{5:^{to_width}}{6:^{invoice_id_width}}{7:>{total_width}}'.format(
                            workday.id,
                            workday.start.date().isoformat(),
                            workday.customer.name,
                            workday.project.name,
                            workday.start.strftime(self.time_format),
                            workday.end.strftime(self.time_format),
                            workday.invoice_id or '',
                            total_output,
                            # Widths
                            id_width=workdays.columns.id.width,
                            date_width=workdays.columns.date.width,
                            customer_width=workdays.columns.customer.width,
                            project_width=workdays.columns.project.width,
                            from_width=workdays.columns.from_date.width,
                            to_width=workdays.columns.to_date.width,
                            invoice_id_width=workdays.columns.invoice_id.width,
                            total_width=total_width
                        )
            return_str += '\n' + divider()

        return return_str


    def invoices(self):
        not_exported_message = 'Not exported'
        invoices = Table()
        invoices.columns.add(Column(name='id',
                                    width=len(max([str(x.id) for x in self.db_query], key=len)) + 3))
        invoices.columns.add(Column(headline='Created on',
                                    width=len(self.db_query[0].created.date().isoformat()) + 6))
        invoices.columns.add(Column(headline='Customer',
                                    width=len(max([x.customer.name for x in self.db_query], key=len)) + 6))
        invoices.columns.add(Column(headline='Year',
                                    width=len(max([x.year if x.year else '' for x in self.db_query], key=len)) + 6))
        invoices.columns.add(Column(headline='Month',
                                    width=len(max([x.month if x.month else '' for x in self.db_query], key=len)) + 6))
        invoices.columns.add(Column(headline='PDF',
                                    width=max(len(max([x.pdf if x.pdf else '' for x in self.db_query], key=len)), len(not_exported_message)) + 6))
        invoices.columns.add(Column(headline='Sent',
                                    width=max(len('Yes'), len('Sent')) + 6))
        invoices.columns.add(Column(headline='Paid',
                                    width=max(len('Yes'), len('Paid')) + 6))
        return_str = divider()
        return_str += '\n'
        return_str += '{0:<{id_width}} {1:<{created_width}} {2:<{customer_width}} {3:<{year_width}} {4:<{month_width}} {5:<{pdf_width}} {6:<{sent_width}} {7:<{paid_width}}'.format(
                         invoices.columns.id.headline,
                         invoices.columns.created_on.headline,
                         invoices.columns.customer.headline,
                         invoices.columns.year.headline,
                         invoices.columns.month.headline,
                         invoices.columns.pdf.headline,
                         invoices.columns.sent.headline,
                         invoices.columns.paid.headline,
                         id_width=invoices.columns.id.width,
                         created_width=invoices.columns.created_on.width,
                         customer_width=invoices.columns.customer.width,
                         year_width=invoices.columns.year.width,
                         month_width=invoices.columns.month.width,
                         pdf_width=invoices.columns.pdf.width,
                         sent_width=invoices.columns.sent.width,
                         paid_width=invoices.columns.paid.width
                         )
        return_str += '\n' + divider()

        # Output for each invoice
        for invoice in self.db_query:
            return_str += '{0:<{id_width}} {1:<{created_width}} {2:<{customer_width}} {3:<{year_width}} {4:<{month_width}} {5:<{pdf_width}} {6:<{sent_width}} {7:<{paid_width}}'.format(
                            invoice.id,
                            invoice.created.date().isoformat(),
                            invoice.customer.name,
                            invoice.year,
                            invoice.month,
                            invoice.pdf or not_exported_message,
                            boolean_yes_or_no(invoice.sent),
                            boolean_yes_or_no(invoice.paid),
                            id_width=invoices.columns.id.width,
                            created_width=invoices.columns.created_on.width,
                            customer_width=invoices.columns.customer.width,
                            year_width=invoices.columns.year.width,
                            month_width=invoices.columns.month.width,
                            pdf_width=invoices.columns.pdf.width,
                            sent_width=invoices.columns.sent.width,
                            paid_width=invoices.columns.paid.width
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
