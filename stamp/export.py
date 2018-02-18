import os

from reportlab.pdfgen import canvas

from __init__ import REPORT_DIR, BASE_DIR
from db import query_for_workdays
from helpers import output_for_total_hours_date_and_wage


def create_pdf(args):
    workdays = query_for_workdays(args=args)

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
                                                                     workday.start.time().isoformat(),
                                                                     workday.end.time().isoformat()))
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
    pdf.drawImage(os.path.join(BASE_DIR, 'logo.png'), width - 100, height - 110, width=100, height=100, mask=[0, 0, 0, 0, 0, 0])
    pdf.showPage()
    pdf.save()
    return
