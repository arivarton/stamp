import os
import sys
import calendar
import operator

from datetime import datetime, timedelta

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Spacer, Table, Paragraph
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER

from .settings import (ORG_NR, FILE_DIR, COMPANY_NAME, COMPANY_ADDRESS,
                       COMPANY_ZIP_CODE, COMPANY_ACCOUNT_NUMBER, MAIL, PHONE,
                       INVOICE_DIR)
from .exceptions import (TooManyMatchesError, ArgumentError, NoMatchesError,
                         NoMatchingDatabaseEntryError,
                         TooManyMatchingDatabaseEntriesError)
from .helpers import output_for_total_hours_date_and_wage, get_month_names
from .formatting import yes_or_no
from .status import Status
from .add import create_invoice
from .mappings import Workday


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
    elif not _selected_month:
        raise NoMatchesError('%s is not an acceptable month format.' % selected_month)
    else:
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
    PAGE_WIDTH, PAGE_HEIGHT = A4

    styles = getSampleStyleSheet()
    header_style = ParagraphStyle('header', alignment=TA_CENTER, fontName='Times-Bold',
                                  textColor='white', backColor='black')
    workday_style = ParagraphStyle('workday', alignment=TA_CENTER, fontName='Times-Roman')
    workday_conclusion_style = ParagraphStyle('workday-conclusion', alignment=TA_CENTER, fontName='Times-Bold')
    tag_header_style = ParagraphStyle('tag-header', alignment=TA_CENTER, fontName='Times-Bold',
                                      fontSize=12)
    tag_style = ParagraphStyle('tag', alignment=TA_CENTER, fontName='Times-Roman')

    logo_file = os.path.join(FILE_DIR, 'logo.png')
    invoice_date = workdays[0].invoice.created
    maturity_date = datetime.now() + timedelta(days=60)
    delivery_date = datetime.now()
    customer_height = PAGE_HEIGHT - 20
    customer_width = 50
    customer_height2 = PAGE_HEIGHT - 130
    customer_width2 = 50
    invoice_height = PAGE_HEIGHT - 130
    invoice_width = PAGE_WIDTH - 170
    bottom_width = 18
    bottom_end_width = PAGE_WIDTH - 108
    bottom_height = 18

    output_hours, __, output_wage = output_for_total_hours_date_and_wage(workdays)
    def myFirstPage(canvas, doc):
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
        canvas.setFont('Times-Bold', 14)
        canvas.drawString(customer_width2, customer_height2,
                          workdays[0].customer.name)
        canvas.setFont('Times-Roman', 9)
        canvas.drawString(customer_width2, customer_height2 - 15, workdays[0].customer.address)
        canvas.drawString(customer_width2, customer_height2 - 26, workdays[0].customer.zip_code)

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
        canvas.saveState()
        # Bottom info
        canvas.setFont('Times-Roman', 9)
        canvas.drawCentredString(PAGE_WIDTH/2.0, bottom_height, output_wage)
        canvas.drawString(bottom_width, bottom_height, COMPANY_NAME)
        canvas.drawString(bottom_end_width, bottom_height, COMPANY_ACCOUNT_NUMBER)
        canvas.restoreState()

    doc = SimpleDocTemplate(file_dir)
    Story = [Spacer(1, 2*inch)]
    workday_header = [[Paragraph('Dato', header_style),
                      Paragraph('Fra', header_style),
                      Paragraph('Til', header_style),
                      Paragraph('Timer', header_style),
                      Paragraph('Lønn', header_style)]]
    Story.append(Table(workday_header, colWidths=100,
                       style=[('LEFTPADDING', (0,0), (-1,-1), 0),
                              ('RIGHTPADDING', (0,0), (-1,-1), 0)]))
    workday_rows = []
    tag_rows = []
    for workday in workdays:
        workday_tags = []
        hours, date, wage = output_for_total_hours_date_and_wage(workday)
        workday_rows.append([Paragraph(date, workday_style),
                             Paragraph(workday.start.time().strftime('%H:%M'), workday_style),
                             Paragraph(workday.end.time().strftime('%H:%M'), workday_style),
                             Paragraph(hours.strip('h'), workday_style),
                             Paragraph(wage, workday_style)])
        for tag in workday.tags:
            workday_tags.append([Paragraph(date + ' ' + tag.recorded.strftime('%H:%M'), tag_header_style)])
            workday_tags.append([Paragraph(tag.tag, tag_style)])
        tag_rows.append([Table(workday_tags, style=[('BOTTOMPADDING', (0,1), (0,1), 12)])])
#            tag_rows.append([Table([[Paragraph(output_date + ' ' + tag.recorded.strftime('%H:%M'), tag_header_style)],
#                                  [Paragraph(tag.tag, tag_style)]])])
    workday_rows.append(['', '', '', Paragraph(output_hours, workday_conclusion_style),
                         Paragraph(output_wage, workday_conclusion_style)])


    # Add workdays to story
    Story.append(Table(workday_rows, colWidths=100,
                       style=[('ROWBACKGROUNDS', (0,0), (-1,-1), [None, 'lightgrey'])]))
    # Add tags to story
    Story.append(Table(tag_rows, colWidths=500,
                       style=[('ROWBACKGROUNDS', (1,1), (-1,-1), [None, 'lightgrey']),
                              ('TOPPADDING', (0,0), (-1,-1), 45)]))

    doc.build(Story, onFirstPage=myFirstPage, onLaterPages=myLaterPages)

    return file_dir


def export_pdf(db, year, month, customer, invoice):
    try:
        save_dir = os.path.join(INVOICE_DIR,
                                # DB name
                                db.session.connection().engine.url.database.split('/')[-1].split('.')[0],
                                customer,
                                year,
                                month)
        pdf_file = create_pdf(invoice.workdays, save_dir, invoice.id)
        invoice.pdf = pdf_file
        invoice.month = month
        invoice.year = year
        print('Saved pdf here: %s' % pdf_file)
        db.session.add(invoice)
    except:
        db.session.delete(invoice)
        raise
    return pdf_file


def export_invoice(db, year, month, customer, project, save_pdf=False):
    export_filter, month = parse_export_filter(month, year, customer, db, project)
    workdays = db.query_db_export_filter('Workday', export_filter).order_by(Workday.start)
    try:
        related_invoice = db.get_related_invoice(year, month)
        workday_ids = [i.id for i in workdays]
        related_invoice_ids = [i.id for i in related_invoice.workdays]
        if workday_ids == related_invoice_ids:
            if save_pdf and related_invoice.pdf:
                yes_or_no('This invoice already has an exported pdf, do you wish to create a new one?',
                          no_message='Canceling...',
                          no_function=sys.exit,
                          no_function_args=(0,),
                          yes_message='Creating new pdf!')
                invoice = related_invoice
            elif save_pdf and not related_invoice.pdf:
                invoice = related_invoice
            else:
                print('Invoice already exists. Append --pdf if you want to export pdf!')
        else:
            print('Old workdays:')
            status_object = Status(related_invoice.workdays)
            print(status_object)
            print('Current workdays:')
            status_object = Status(workdays)
            print(status_object)
            invoice = yes_or_no('Invoice already exists for this month but does not contain the same work days/hours. Do you wish to create a new invoice for this month? This cannot be undone!',
                                no_message='Canceling...',
                                no_function=sys.exit,
                                no_function_args=(0,),
                                yes_message='Redoing invoice for specified month!',
                                yes_function=create_invoice,
                                yes_function_args=(db, workdays, customer, year,
                                                   month))
    except NoMatchingDatabaseEntryError:
        status_object = Status(workdays)
        print(status_object)
        invoice = yes_or_no('Do you wish to create a invoice containing these workdays?',
                            no_message='Canceling...',
                            no_function=sys.exit,
                            no_function_args=(0,),
                            yes_message='Creating new invoice!',
                            yes_function=create_invoice,
                            yes_function_args=(db, workdays, customer, year,
                                               month))
    except KeyboardInterrupt:
        print('Canceling...')
        sys.exit(0)
    if save_pdf:
        return export_pdf(db, year, month, customer, invoice)
