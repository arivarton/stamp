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
    db.add(workday)

def edit_customer(db, workday_id, edit):
    pass

def edit_project(db, workday_id, edit):
    pass
