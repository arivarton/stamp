from ..parents import StatusColumn
from ...helpers import output_for_total_hours_date_and_wage, get_terminal_width

class ID(StatusColumn):
    def __init__(self, workdays):
        super().__init__()
        self.value = workday.id

    def width(self):
        return len(max([str(x.id) for x in workdays], key=len)) + 2



class Date(StatusColumn):
    def __init__(self, workdays):
        super().__init__()
        self.headline = 'Date'
        self.width = max(len(workdays[0].start.date().isoformat()), len(self.headline)) + 3
        __, date, __ = output_for_total_hours_date_and_wage(workday)
        self.value = date


class Customer(StatusColumn):
    def __init__(self, workdays):
        super().__init__()
        self.headline = 'Customer'
        self.width = max(len(max([x.customer.name for x in workdays], key=len)), len(self.headline)) + 2
        self.values.append(workday.customer.name)


class Project(StatusColumn):
    def __init__(self, workdays):
        super().__init__()
        self.headline = 'Project'
        self.width = max(len(max([x.project.name for x in workdays], key=len)), len(self.headline)) + 4
        self.values.append(workday.project.name)


class From(StatusColumn):
    def __init__(self, workdays):
        super().__init__()
        self.headline = 'From'
        self.width = max(len(workdays[0].start.strftime(self.time_format)), len(self.headline))
        self.value = workday.start.strftime(self.time_format)


class To(StatusColumn):
    def __init__(self, workdays):
        super().__init__()
        self.headline = 'To'
        self.width = max(len(workdays[0].end.strftime(self.time_format)), len(self.headline))
        self.value = workday.end.strftime(self.time_format)


class InvoiceID(StatusColumn):
    def __init__(self, workday):
        super().__init__()
        self.headline = 'Invoice ID'
        self.width = max(len(max([str(x.invoice_id) for x in workdays], key=len)), len(self.headline))
        self.alignment = '^'
        self.value = workday.invoice_id


class TotalWorkday(StatusColumn):
    def __init__(self, items, workday):
        super().__init__()
        self.headline = 'Total'
        self.width = get_terminal_width() - (sum([value.width for value in items]) + 11)
        self.alignment = '>'
        total_hours, __, total_wage = output_for_total_hours_date_and_wage(workday)
        self.value = f'{total_hours} for {total_wage}'


class Tag(ID):
    def __init__(self, workdays):
        # Get width from id
        super().__init__(workdays)
        self.alignment = '<'
        self.values.append([[tag.id, tag.recorded.strftime(self.time_format), tag.tag] for tag in workday.tags])


class Workday(object):
    def __init__(self, workday):
        self.id = ID(workday)
        self.date = Date(workday)
        self.customer = Customer(workday)
        self.project = Project(workday)
        self.from_time = From(workday)
        self.to_time = To(workday)
        self.invoice_id = InvoiceID(workday)
        # Anything after this attribute will not be added to total width in
        # workday
        self.total_workday = TotalWorkday(self.__dict__.values(), workday)
        self.total_columns = len(self.__dict__.values())
        self.tags = Tag(workday)
        self.total_hours, __, self.total_wage = output_for_total_hours_date_and_wage(workday)
