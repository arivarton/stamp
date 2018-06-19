import os
import sys
import calendar
import operator

from datetime import datetime, timedelta

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Spacer, Table
from reportlab.lib.units import inch

from .settings import (ORG_NR, FILE_DIR, COMPANY_NAME, COMPANY_ADDRESS,
                       COMPANY_ZIP_CODE, COMPANY_ACCOUNT_NUMBER, MAIL, PHONE)
from .exceptions import (TooManyMatchesError, ArgumentError,
                         NoMatchingDatabaseEntryError, TooManyMatchingDatabaseEntriesError)
from .helpers import output_for_total_hours_date_and_wage, get_month_names


def parse_export_filter(selected_month, selected_year, selected_customer,
                        db, selected_project=None):
    export_filter = dict()
    # Validate month
    _selected_month = list()
    for month in get_month_names():
        if month.startswith(selected_month.capitalize()):
            _selected_month.append(month)
    if len(_selected_month) > 1:
        raise TooManyMatchesError('Refine month argument! These months are currently matching: %s.' %
                                  ', '.join(_selected_month))
    selected_month = ''.join(_selected_month)

    # Validate year
    try:
        date_from = datetime.strptime('%s %s' % (selected_month, selected_year),
                                      '%B %Y')
        _month_days = calendar.monthrange(date_from.year, date_from.month)[1]
        date_to = date_from + timedelta(days=_month_days)
    except ValueError:
        raise ArgumentError('Year argument format wrong! This is the correct format: YYYY. For example: 2018.')

    export_filter.update({'start': {'op_func': operator.ge, 'value': date_from},
                          'end': {'op_func': operator.lt, 'value': date_to}})

    try:
        selected_customer = db.get_one_db_entry('Customer', 'name', selected_customer)
    except NoMatchingDatabaseEntryError as _err_msg:
        print(_err_msg)
        sys.exit(0)
    except TooManyMatchingDatabaseEntriesError as _err_msg:
        print(_err_msg)
        sys.exit(0)
    export_filter.update({'customer_id': {'op_func': operator.eq,
                                          'value': selected_customer.id}})

    # Validate project
    if selected_project:
        try:
            selected_project = db.get_one_db_entry('Project', 'name', selected_project)
        except NoMatchingDatabaseEntryError as _err_msg:
            print(_err_msg)
            sys.exit(0)
        except TooManyMatchingDatabaseEntriesError as _err_msg:
            print(_err_msg)
            sys.exit(0)
        export_filter.update({'project_id': {'op_func': operator.eq,
                                             'value': selected_project.id}})

    return export_filter, selected_month


def create_pdf(workdays, save_dir, invoice_id=None): # NOQA
    if invoice_id:
        file_name = str(invoice_id) + '-invoice.pdf'
    else:
        file_name = 'report.pdf'

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    file_dir = os.path.join(save_dir, file_name)

    # Document settings
    PAGE_HEIGHT = A4[1]
    PAGE_WIDTH = A4[0]
    logo_file = os.path.join(FILE_DIR, 'logo.png')
    invoice_date = workdays[0].invoice.created
    maturity_date = datetime.now() + timedelta(days=60)
    delivery_date = datetime.now()
    customer_height = PAGE_HEIGHT - 20
    customer_width = 50
    customer_height2 = PAGE_HEIGHT - 130
    customer_width2 = 50
    invoice_height = PAGE_HEIGHT - 130
    invoice_width = PAGE_WIDTH - 150
    bottom_width = 18
    bottom_end_width = PAGE_WIDTH - 108
    bottom_height = 18

    def myFirstPage(canvas, doc):
        __, __, output_wage = output_for_total_hours_date_and_wage(workdays)
        canvas.saveState()
        if os.path.isfile(logo_file):
            canvas.drawImage(logo_file, PAGE_WIDTH - 110, customer_height - 75, width=81, height=81, mask=[0, 0, 0, 0, 0, 0],
                             preserveAspectRatio=True)

        # Sellers customer info
        canvas.setFont('Times-Bold', 12)
        canvas.drawString(customer_width, customer_height, COMPANY_NAME)
        canvas.setFont('Times-Bold', 9)
        canvas.drawString(customer_width, customer_height - 37, "Org nr:")
        canvas.drawString(customer_width, customer_height - 48, "Epost:")
        canvas.drawString(customer_width, customer_height - 59, "Tlf:")
        canvas.setFont('Times-Roman', 9)
        canvas.drawString(customer_width, customer_height - 10, COMPANY_ADDRESS)
        canvas.drawString(customer_width, customer_height - 21, COMPANY_ZIP_CODE)
        canvas.drawString(customer_width + 50, customer_height - 37, ORG_NR)
        canvas.drawString(customer_width + 50, customer_height - 48, MAIL)
        canvas.drawString(customer_width + 50, customer_height - 59, PHONE)

        # Buyers customer info
        canvas.setFont('Times-Bold', 12)
        canvas.drawString(customer_width2, customer_height2,
                          workdays[0].customer.name)
        canvas.setFont('Times-Roman', 9)
        canvas.drawString(customer_width2, customer_height2 - 10, workdays[0].customer.address)
        canvas.drawString(customer_width2, customer_height2 - 21, workdays[0].customer.zip_code)

        # Invoice
        canvas.setFont('Times-Bold', 14)
        canvas.drawString(invoice_width, invoice_height, "Faktura")
        canvas.setFont('Times-Bold', 9)
        canvas.drawString(invoice_width, invoice_height - 15, "Kunde nr:")
        canvas.drawString(invoice_width, invoice_height - 26, "Faktura nr:")
        canvas.drawString(invoice_width, invoice_height - 37, "Faktura dato:")
        canvas.drawString(invoice_width, invoice_height - 48, "Forfalls dato:")
        canvas.drawString(invoice_width, invoice_height - 59, "Leverings dato:")
        canvas.setFont('Times-Roman', 9)
        canvas.drawString(invoice_width + 80, invoice_height - 15, str(workdays[0].customer.id))
        canvas.drawString(invoice_width + 80, invoice_height - 26, str(invoice_id))
        canvas.drawString(invoice_width + 80, invoice_height - 37, invoice_date.strftime('%d.%m.%Y'))
        canvas.drawString(invoice_width + 80, invoice_height - 48, maturity_date.strftime('%d.%m.%Y'))
        canvas.drawString(invoice_width + 80, invoice_height - 59, delivery_date.strftime('%d.%m.%Y'))

        # Bottom info
        canvas.setFont('Times-Roman', 9)
        canvas.drawCentredString(PAGE_WIDTH/2.0, bottom_height, output_wage)
        canvas.drawString(bottom_width, bottom_height, COMPANY_NAME)
        canvas.drawString(bottom_end_width, bottom_height, COMPANY_ACCOUNT_NUMBER)

        canvas.restoreState()

    def myLaterPages(canvas, doc):
        __, __, output_wage = output_for_total_hours_date_and_wage(workdays)
        canvas.saveState()
        # Bottom info
        canvas.setFont('Times-Roman', 9)
        canvas.drawCentredString(PAGE_WIDTH/2.0, bottom_height, output_wage)
        canvas.drawString(bottom_width, bottom_height, COMPANY_NAME)
        canvas.drawString(bottom_end_width, bottom_height, COMPANY_ACCOUNT_NUMBER)
        canvas.restoreState()

    doc = SimpleDocTemplate(file_dir)
    Story = [Spacer(1, 2*inch)]
    workday_info = [['Dato', 'Fra', 'Til', 'Timer', 'Lønn']]
    for workday in workdays:
        output_hours, output_date, output_wage = output_for_total_hours_date_and_wage(workday)
        workday_info.append([output_date,
                             workday.start.time().strftime('%H:%M'),
                             workday.end.time().strftime('%H:%M'),
                             output_hours.strip('h'),
                             output_wage])
        for tag in workday.tags:
            workday_info.append(['', tag.recorded.strftime('%H:%M'), tag.tag])
    t = Table(workday_info, colWidths=100, style=[
        ('FONTNAME', (0, 0), (-1, -1), 'Times-Roman'),
        ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold')])
    Story.append(t)
    doc.build(Story, onFirstPage=myFirstPage, onLaterPages=myLaterPages)

    return file_dir
