import os
import sys
import calendar
import operator

from datetime import datetime, timedelta

from reportlab.pdfgen import canvas

from .settings import FILE_DIR, REPORT_DIR
from .db import get_one_db_entry, query_db_export_filter
from .exceptions import TooManyMatchesError, ArgumentError, NoMatchingDatabaseEntryError
from .helpers import output_for_total_hours_date_and_wage


def _parse_export_filter(selected_month, selected_year, selected_customer=None,
                         selected_project=None):
    export_filter = dict()
    # Validate month
    _valid_months = ['January', 'February', 'March', 'April', 'May', 'June',
                     'July', 'August', 'September', 'October', 'November',
                     'December']
    _selected_month = list()
    for month in _valid_months:
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

    # Validate customer
    if selected_customer:
        try:
            selected_customer = get_one_db_entry('Customer', 'name', selected_customer)
        except NoMatchingDatabaseEntryError as _err_msg:
            print(_err_msg)
            sys.exit(0)
        export_filter.update({'customer_id': {'op_func': operator.eq,
                                              'value': selected_customer.id}})

    # Validate project
    if selected_project:
        try:
            selected_project = get_one_db_entry('Project', 'name', selected_project)
        except NoMatchingDatabaseEntryError as _err_msg:
            print(_err_msg)
            sys.exit(0)
        export_filter.update({'project_id': {'op_func': operator.eq,
                                             'value': selected_project.id}})

    return export_filter


def create_pdf(args):
    export_filter = _parse_export_filter(args.month, args.year, args.customer,
                                         args.project)
    try:
        workdays = query_db_export_filter('Workday', export_filter)
    except NoMatchingDatabaseEntryError as _err_msg:
        print(_err_msg)
        sys.exit(0)

    output_filename = os.path.join(REPORT_DIR, 'report.pdf')

    # A4 paper, 210mm*297mm displayed on a 96dpi monitor
    width = 210 / 25.4 * 96
    height = 297 / 25.4 * 96

    pdf = canvas.Canvas(output_filename, pagesize=(width, height))
    pdf.setStrokeColorRGB(0, 0, 0)
    pdf.setFillColorRGB(0, 0, 0)
    font_size = 12
    font_padding = 20
    pdf.setFont("Helvetica", font_size)
    height_placement = height - font_size
    for workday in workdays:
        output_hours, output_date, output_wage = output_for_total_hours_date_and_wage(workday)
        height_placement -= font_size
        # Date
        pdf.drawString(font_padding, height_placement, '%s %s-%s' % (output_date,
                                                                     workday.start.time().strftime('%H:%M'),
                                                                     workday.end.time().strftime('%H:%M')))
        height_placement -= font_size
        # Worktime
        pdf.drawString(font_padding, height_placement, 'Total hours: %s' % (output_hours))
        height_placement -= font_size
        pdf.drawString(font_padding, height_placement, 'Wage: %s' % (output_wage))
        for tag in workday.tags:
            height_placement -= font_size
            pdf.drawString(font_padding, height_placement, '%s - %s' % (tag.recorded.time().isoformat(), tag.tag))
        height_placement -= font_size
    output_total_hours, __, output_total_wage = output_for_total_hours_date_and_wage(workdays)
    height_placement -= font_size * 2
    pdf.drawString(font_padding, height_placement, 'Total hours: %s' % (output_total_hours))
    height_placement -= font_size
    pdf.drawString(font_padding, height_placement, 'Total wage: %s' % (output_total_wage))
    logo_file = os.path.join(FILE_DIR, 'logo.png')
    if os.path.isfile(logo_file):
        pdf.drawImage(logo_file, width - 100, height - 110, width=100, height=100, mask=[0, 0, 0, 0, 0, 0])
    pdf.showPage()
    pdf.save()
    return
