import sys
import re

def edit_workday(db, id, date=None, time=None, comment=None, customer=None):
    workday = db.get('Workday', id)
    if date:
        workday.date = date
    if time:
        workday.time = time
    if comment:
        workday.comment = comment
    if customer:
        workday.customer = customer
    return workday

def edit_customer(db, id, name=None, contact=None, org_nr=None, address=None,
                  zip_code=None, mail=None, phone=None):
    customer = db.get('Customer', id)
    if name:
        customer.name = name
    if contact:
        customer.contact = contact
    if org_nr:
        customer.org_nr = org_nr
    if address:
        customer.address = address
    if zip_code:
        customer.zip_code = zip_code
    if mail:
        customer.mail = mail
    if phone:
        customer.phone = mail
    return customer

def edit_project(db, id, name=None, link=None):
    project = db.get('Project', id)
    if name:
        project.name = name
    if link:
        project.link = link
    return project

def edit_invoice(db, id, paid=False, sent=False):
    invoice = db.get('Invoice', id)
    if paid:
        if invoice.paid:
            invoice.paid = False
        else:
            invoice.paid = True
    if sent:
        if invoice.sent:
            invoice.sent = False
        else:
            invoice.sent = True
    return invoice
