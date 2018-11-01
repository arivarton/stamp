import sys
import re

def edit_workday(db, id, date=None, time=None, comment=None, customer=None):
    workday = args.db.query_for_workdays(args.id)
    if edit.date:
        workday.date = args.date
    if edit.time:
        workday.time = args.time
    if edit.comment:
        workday.comment = args.comment
    if edit.customer:
        workday.customer = args.customer
    return workday

def edit_customer(db, id, name=None, contact=None, org_nr=None, address=None,
                  zip_code=None, mail=None, phone=None):
    customer = db.query_for_customer(id)
    if args.name:
        customer.name = args.name
    if args.contact:
        customer.contact = args.contact
    if args.org_nr:
        customer.org_nr = args.org_nr
    if args.address:
        customer.address = args.address
    if args.zip_code:
        customer.zip_code = args.zip_code
    if args.mail:
        customer.mail = args.mail
    if args.phone:
        customer.phone = args.mail
    return customer

def edit_project(db, id, name=None, link=None):
    project = db.query_for_project(id)
    if args.name:
        project.name = args.name
    if args.link:
        project.link = args.link
    return project

def edit_invoice(db, id, paid=False, sent=False):
    db_query = db.get_invoices(id)
    if paid:
        if db_query.paid:
            db_query.paid = False
        else:
            db_query.paid = True
    if sent:
        if db_query.sent:
            db_query.sent = False
        else:
            db_query.sent = True
    return db_query
