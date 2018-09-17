import re


def edit_regex_resolver(edit_string):
    return_value = {'date': re.findall('date=[\'"]?([^\'",]*)', edit_string) or None,
                    'time': re.findall('time=[\'"]?([^\'",]*)', edit_string) or None,
                    'comment': re.findall('comment=[\'"]?([^\'",]*)', edit_string) or None,
                    'customer': re.findall('customer=[\'"]?([^\'",]*)', edit_string) or None}

    return return_value


def _edit_tag():
    pass


def edit_workday(db, workday_id, edit):
    workday = db.query_for_workdays(workday_id=workday_id)
    if edit['date']:
        workday.date = edit['date'][0]
    if edit['time']:
        workday.time = edit['time'][0]
    if edit['comment']:
        workday.comment = edit['comment'][0]
    if edit['customer']:
        workday.customer = edit['customer'][0]
    return workday

def edit_customer(db, args):
    customer = db.query_for_customer(args.id)
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

def edit_project(db, args):
    project = db.query_for_project(args.id)
    if args.name:
        project.name = args.name
    if args.link:
        project.link = args.link
    return project
