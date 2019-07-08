import os
import sys
import calendar

from datetime import datetime, timedelta

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Spacer, Table, Paragraph, PageBreak
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER

from .settings import (FILE_DIR,
                       INVOICE_DIR)
from .exceptions import (TooManyMatchesError, ArgumentError, NoMatchesError,
                         NoMatchingDatabaseEntryError,
                         TooManyMatchingDatabaseEntriesError)
from .helpers import calculate_workhours, calculate_wage, get_month_names, error_handler
from .formatting import yes_or_no
from .status import Status
from .add import create_invoice
from .mappings import Workday, Customer, Project
from .db import Database

__all__ = ['export_invoice']


class GetExportFilter(object):  # pylint: disable=too-few-public-methods
    def __init__(self, db: Database, year: int, month: str, customer: str, project: str):
        self.db = db
        self.year = year
        self.month = self._validate_month(month)
        self.customer = self._get_customer(customer)
        self.project = self._get_project(project)
        self.start = self._get_start(self.month, self.year)
        self.end = self._get_end(self.start)

    def _validate_month(self, month_name):
        # Validate month
        months = list()
        for month in get_month_names():
            if month.startswith(month_name.capitalize()):
                months.append(month)
        if len(months) > 1:
            raise TooManyMatchesError('Refine month argument! These months are currently matching: %s.' %
                                      ', '.join(months))
        elif not months:
            raise NoMatchesError('%s is not an acceptable month format. These are the month names to match: %s.' % (month_name, ', '.join(get_month_names())))
        else:
            return ''.join(months)

    def _get_customer(self, customer):
        try:
            customer = self.db.get('Customer').filter(Customer.name == customer).first()
        except NoMatchingDatabaseEntryError as err_msg:
            error_handler(err_msg)
        return customer

    def _get_project(self, project):
        try:
            project = self.db.get('Project').filter(Project.name == project).first()
        except NoMatchingDatabaseEntryError as err_msg:
            error_handler(err_msg)
        return project

    def _get_start(self, month, year):
        return datetime.strptime('%s %s' % (month, year),
                                 '%B %Y')

    def _get_end(self, start):
        _month_days = calendar.monthrange(start.year, start.month)[1]
        return start + timedelta(days=_month_days)


def create_pdf(workdays, save_dir, config, invoice_id=None): # NOQA
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
    output_hours = sum([calculate_workhours(w.start, w.end) for w in workdays])
    output_wage = calculate_wage(output_hours, config.values.wage_per_hour.value)

    def myFirstPage(canvas, doc):
        canvas.saveState()
        if os.path.isfile(logo_file):
            canvas.drawImage(logo_file, PAGE_WIDTH - 110, customer_height - 75, width=81, height=81, mask=[0, 0, 0, 0, 0, 0],
                             preserveAspectRatio=True)

        # Sellers customer info
        canvas.setFont('Times-Bold', 12)
        canvas.drawString(customer_width, customer_height, config.values.company_name.value)
        canvas.setFont('Times-Bold', 9)
        canvas.drawString(customer_width, customer_height - 37, _("Organization number:"))
        canvas.drawString(customer_width, customer_height - 48, "Epost:")
        canvas.drawString(customer_width, customer_height - 59, "Tlf:")
        canvas.setFont('Times-Roman', 9)
        canvas.drawString(customer_width, customer_height - 10, config.values.company_address.value)
        canvas.drawString(customer_width, customer_height - 21, config.values.company_zip.value)
        canvas.drawString(customer_width + 50, customer_height - 37, config.values.organization_number.value)
        canvas.drawString(customer_width + 50, customer_height - 48, config.values.mail_address.value)
        canvas.drawString(customer_width + 50, customer_height - 59, config.values.phone_number.value)

        # Buyers customer info
        canvas.setFont('Times-Bold', 14)
        canvas.drawString(customer_width2, customer_height2,
                          workdays[0].customer.name)
        canvas.setFont('Times-Roman', 9)
        canvas.drawString(customer_width2, customer_height2 - 15, str(workdays[0].customer.address))
        canvas.drawString(customer_width2, customer_height2 - 26, str(workdays[0].customer.zip_code))

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
        canvas.drawCentredString(PAGE_WIDTH/2.0, bottom_height, str(round(output_wage, 2)))
        canvas.drawString(bottom_width, bottom_height, config.values.company_name.value)
        canvas.drawString(bottom_end_width, bottom_height, config.values.company_account_number.value)

        canvas.restoreState()

    def myLaterPages(canvas, doc):
        canvas.saveState()
        # Bottom info
        canvas.setFont('Times-Roman', 9)
        canvas.drawCentredString(PAGE_WIDTH/2.0, bottom_height, str(round(output_wage, 2)))
        canvas.drawString(bottom_width, bottom_height, config.values.company_name.value)
        canvas.drawString(bottom_end_width, bottom_height, config.values.company_account_number.value)
        canvas.restoreState()

    def new_page(canvas, doc):
        canvas.showPage()
        canvas.restoreState()

    doc = SimpleDocTemplate(file_dir)
    Story = [Spacer(1, 2*inch)]
    workday_header = [[Paragraph('Dato', header_style),
                      Paragraph('Prosjekt', header_style),
                      Paragraph('Fra', header_style),
                      Paragraph('Til', header_style),
                      Paragraph('Timer', header_style),
                      Paragraph('Å betale', header_style)]]
    Story.append(Table(workday_header, colWidths=100,
                       style=[('LEFTPADDING', (0,0), (-1,-1), 0),
                              ('RIGHTPADDING', (0,0), (-1,-1), 0)]))
    workday_rows = []
    tag_rows = []
    for workday in workdays:
        workday_tags = []
        hours = calculate_workhours(workday.start, workday.end)
        workday_rows.append([Paragraph(workday.start.date().isoformat(), workday_style),
                             Paragraph(workday.project.name, workday_style),
                             Paragraph(workday.start.time().strftime('%H:%M'), workday_style),
                             Paragraph(workday.end.time().strftime('%H:%M'), workday_style),
                             Paragraph(str(round(hours, 2)), workday_style),
                             Paragraph('%s %s' % (str(round(calculate_wage(hours, config.values.wage_per_hour.value), 2)), config.values.currency.value), workday_style)])
        for tag in workday.tags:
            workday_tags.append([Table([[Paragraph(workday.start.date().isoformat() + ' ' + tag.recorded.strftime('%H:%M'), tag_header_style)],
                                [Paragraph(tag.tag, tag_style)]], style=[('LINEBELOW', (0,0), (0,0), 0.1, 'black'),
                                                                         ('BOTTOMPADDING', (0,1), (-1,-1), 12)])])
        if workday_tags:
            tag_rows.append([Table(workday_tags, style=[('BOTTOMPADDING', (-1,-1), (-1,-1), 45)])])
    workday_rows.append(['', '', '', '', Paragraph(str(round(output_hours, 2)), workday_conclusion_style),
                         Paragraph('%s %s' % (str(round(output_wage, 2)), config.values.currency.value), workday_conclusion_style)])


    # Add workdays to story
    Story.append(Table(workday_rows, colWidths=100,
                       style=[('ROWBACKGROUNDS', (0,0), (-1,-1), [None, 'lightgrey'])]))

    Story.append(PageBreak())

    # Add tags to story
    if tag_rows:
        Story.append(Table(tag_rows, colWidths=500))

    doc.build(Story, onFirstPage=myFirstPage, onLaterPages=myLaterPages)

    return file_dir


def export_pdf(db, year, month, customer, invoice, config):
    try:
        save_dir = os.path.join(INVOICE_DIR,
                                # DB name
                                db.session.connection().engine.url.database.split('/')[-1].split('.')[0],
                                customer,
                                str(year),
                                month)
        pdf_file = create_pdf(invoice.workdays, save_dir, config, invoice.id)
        invoice.pdf = pdf_file
        invoice.month = month
        invoice.year = year
        print('Saved pdf here: %s' % pdf_file)
        db.session.add(invoice)
    except:
        db.session.delete(invoice)
        raise
    return pdf_file


def export_invoice(db, year, month, customer, project, config, save_pdf=False, ask=True):
    export_filter = GetExportFilter(db, year, month, customer, project)
    workdays = db.get('Workday').filter(Workday.start >= export_filter.start,
                                        Workday.end < export_filter.end,
                                        Workday.customer_id == export_filter.customer.id)
    if project:
        workdays.filter(Workday.project_id == export_filter.project.id)
    workdays.order_by(Workday.start)

    try:
        related_invoice = db.get_related_invoice(year, export_filter.month)
        workday_ids = [i.id for i in workdays]
        related_invoice_ids = [i.id for i in related_invoice.workdays]
        if workday_ids == related_invoice_ids:
            if save_pdf and related_invoice.pdf:
                if ask:
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
            status_object = Status(related_invoice.workdays, config)
            print(status_object)
            print('Current workdays:')
            status_object = Status(workdays, config)
            print(status_object)
            if ask:
                invoice = yes_or_no('Invoice already exists for this month but does not contain the same work days/hours. Do you wish to create a new invoice for this month? This cannot be undone!',
                                    no_message='Canceling...',
                                    no_function=sys.exit,
                                    no_function_args=(0,),
                                    yes_message='Redoing invoice for specified month!',
                                    yes_function=create_invoice,
                                    yes_function_args=(db, workdays, customer, year,
                                                       export_filter.month))
            else:
                invoice = create_invoice(db, workdays, customer, year, export_filter.month)
    except NoMatchingDatabaseEntryError:
        status_object = Status(workdays, config)
        print(status_object)
        if ask:
            invoice = yes_or_no('Do you wish to create a invoice containing these workdays?',
                                no_message='Canceling...',
                                no_function=sys.exit,
                                no_function_args=(0,),
                                yes_message='Creating new invoice!',
                                yes_function=create_invoice,
                                yes_function_args=(db, workdays, customer, year,
                                                   export_filter.month))
        else:
            invoice = create_invoice(db, workdays, customer, year, export_filter.month)
    except KeyboardInterrupt:
        print('Canceling...')
        sys.exit(0)
    if save_pdf:
        return export_pdf(db, year, export_filter.month, customer, invoice, config)
