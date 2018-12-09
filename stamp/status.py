import sys
from sqlalchemy.orm.query import Query
from .helpers import output_for_total_hours_date_and_wage, get_terminal_width
from .formatting import divider


class StatusColumn(object):
    def __init__(self):
        self.headline = ''
        self.width = 5
        self.alignment = '<'
        self.values = list()
        self.time_format = '%H:%M'
        self.left_margin = 0
        self.right_margin = 1
        self.selected_workday = 0

    def __str__(self):
        return '{0}{1:{alignment}{width}}{2}'.format(self.left_margin*' ',
                                                     str(self.values[self.selected_workday]),
                                                     self.right_margin*' ',
                                                     alignment=self.alignment,
                                                     width=self.width)

    def __iter__(self):
        self.selected_workday = 0
        return self

    def __next__(self):
        if self.selected_workday < len(self.values):
            return_value = self.__str__()
            self.selected_workday += 1
            return return_value
        else:
            raise StopIteration

    def add_value(self, value):
        self.values.append(value)

    def get_headline(self):
        return '{0}{1:{alignment}{width}}{2}'.format(self.left_margin*' ',
                                                     str(self.headline),
                                                     self.right_margin*' ',
                                                     alignment=self.alignment,
                                                     width=self.width)


class ID(StatusColumn):
    def __init__(self, workdays):
        super().__init__()
        self.width = len(max([str(x.id) for x in workdays], key=len)) + 2
        for workday in workdays:
            self.values.append(workday.id)


class Date(StatusColumn):
    def __init__(self, workdays):
        super().__init__()
        self.headline = 'Date'
        self.width = max(len(workdays[0].start.date().isoformat()), len(self.headline)) + 3
        for workday in workdays:
            __, date, __ = output_for_total_hours_date_and_wage(workday)
            self.values.append(date)


class Customer(StatusColumn):
    def __init__(self, workdays):
        super().__init__()
        self.headline = 'Customer'
        self.width = max(len(max([x.customer.name for x in workdays], key=len)), len(self.headline)) + 2
        for workday in workdays:
            self.values.append(workday.customer.name)


class Project(StatusColumn):
    def __init__(self, workdays):
        super().__init__()
        self.headline = 'Project'
        self.width = max(len(max([x.project.name for x in workdays], key=len)), len(self.headline)) + 4
        for workday in workdays:
            self.values.append(workday.project.name)


class From(StatusColumn):
    def __init__(self, workdays):
        super().__init__()
        self.headline = 'From'
        self.width = max(len(workdays[0].start.strftime(self.time_format)), len(self.headline))
        for workday in workdays:
            self.values.append(workday.start.strftime(self.time_format))


class To(StatusColumn):
    def __init__(self, workdays):
        super().__init__()
        self.headline = 'To'
        self.width = max(len(workdays[0].end.strftime(self.time_format)), len(self.headline))
        for workday in workdays:
            if workday.end:
                self.values.append(workday.end.strftime(self.time_format))
            else:
                self.values.append('')


class InvoiceID(StatusColumn):
    def __init__(self, workdays):
        super().__init__()
        self.headline = 'Invoice ID'
        self.width = max(len(max([str(x.invoice_id) for x in workdays], key=len)), len(self.headline))
        self.alignment = '^'
        for workday in workdays:
            self.values.append(workday.invoice_id or '')


class TotalWorkday(StatusColumn):
    def __init__(self, items, workdays):
        super().__init__()
        self.headline = 'Total'
        self.width = get_terminal_width() - (sum([value.width for value in items]) + 11)
        self.alignment = '>'
        for workday in workdays:
            total_hours, __, total_wage = output_for_total_hours_date_and_wage(workday)
            self.values.append(total_hours + ' for ' + total_wage)


class Tag(ID):
    def __init__(self, workdays):
        # Get width from id
        super().__init__(workdays)
        self.alignment = '<'
        for workday in workdays:
            self.values.append([[tag.id, tag.recorded.strftime(self.time_format), tag.tag] for tag in workday.tags])

class PopulatedObject(object):
    def __init__(self, object, table):
        if table == 'workday':
            self.id = ID(object)
            self.date = Date(object)
            self.customer = Customer(object)
            self.project = Project(object)
            self.from_time = From(object)
            self.to_time = To(object)
            self.invoice_id = InvoiceID(object)
            # Anything after this attribute will not be added to total width in
            # workday
            self.total_workday = TotalWorkday(self.__dict__.values(), object)
            self.total_columns = len(self.__dict__.values())
            self.tags = Tag(object)
            self.total_hours, __, self.total_wage = output_for_total_hours_date_and_wage(object)
            self.table = 'workday'
        elif table == 'invoice':
            self.table = 'invoice'



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
        # Headlines
        date_headline = 'Date'
        customer_headline = 'Customer'
        project_headline = 'Project'
        from_headline = 'From'
        to_headline = 'To'
        invoice_id_headline = 'Invoice ID'
        total_workday_headline = 'Total'

        # Width for columns
        widths = {
            'id': len(max([str(x.id) for x in self.db_query], key=len)) + 2,
            'date': max(len(self.db_query[0].start.date().isoformat()), len(date_headline)) + 3,
            'customer': max(len(max([x.customer.name for x in self.db_query], key=len)), len(customer_headline)) + 2,
            'project': max(len(max([x.project.name for x in self.db_query], key=len)), len(project_headline)) + 4,
            'from': max(len(self.db_query[0].start.strftime(self.time_format)), len(from_headline)),
            'to': max(len(self.db_query[0].end.strftime(self.time_format)), len(to_headline)),
            'invoice_id': max(len(max([str(x.invoice_id) for x in self.db_query], key=len)), len(invoice_id_headline))
        }


        return_str = divider()
        return_str += '\n'
        # TODO:
        return_str += '{0:<{id_width}} {1:<{date_width}} {2:<{customer_width}} {3:<{project_width}} {4:<{from_width}} {5:<{to_width}} {6:^{invoice_id_width}} {7:>{total_width}}'.format(
                         '',
                         date_headline,
                         customer_headline,
                         project_headline,
                         from_headline,
                         to_headline,
                         invoice_id_headline,
                         total_workday_headline,
                         id_width=widths['id'],
                         date_width=widths['date'],
                         customer_width=widths['customer'],
                         project_width=widths['project'],
                         from_width=widths['from'],
                         to_width=widths['to'],
                         invoice_id_width=widths['invoice_id'],
                         total_width=sum(widths.values()) + 11
                         )
        return_str += '\n' + divider()

        # Output for each workday
        for workday in self.db_query:
            total_time, date, total_owed = output_for_total_hours_date_and_wage(workday)
            total_output = total_time + ' for ' + total_owed,
            total_width = 1
            return_str += '{0:<{id_width}} {1:<{date_width}} {2:<{customer_width}} {3:<{project_width}} {4:<{from_width}} {5:<{to_width}} {6:^{invoice_id_width}} {7:>{total_width}}'.format(
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
