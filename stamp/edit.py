import sys
import re

def edit_workday(args):
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

def edit_customer(args):
    customer = args.db.query_for_customer(args.id)
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

def edit_project(args):
    project = args.db.query_for_project(args.id)
    if args.name:
        project.name = args.name
    if args.link:
        project.link = args.link
    return project

def edit_invoice(args):
    if args.paid:
        if args.db_query.paid:
            args.db_query.paid = False
        else:
            args.db_query.paid = True
    if args.sent:
        if args.db_query.sent:
            args.db_query.sent = False
        else:
            args.db_query.sent = True
    return args.db_query
