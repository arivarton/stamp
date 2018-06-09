import re

from . import DB_SESSION
from .db import query_for_workdays


def edit_regex_resolver(edit_string):
    return_value = {'date': re.findall('date=[\'"]?([^\'",]*)', edit_string) or None,
                    'time': re.findall('time=[\'"]?([^\'",]*)', edit_string) or None,
                    'comment': re.findall('comment=[\'"]?([^\'",]*)', edit_string) or None,
                    'customer': re.findall('customer=[\'"]?([^\'",]*)', edit_string) or None}

    return return_value


def _edit_tag():
    pass


def edit_workday(args):
    workday = query_for_workdays(workday_id=args.id)
    if args.edit['date']:
        workday.date = args.edit['date'][0]
    if args.edit['time']:
        workday.time = args.edit['time'][0]
    if args.edit['comment']:
        workday.comment = args.edit['comment'][0]
    if args.edit['customer']:
        workday.customer = args.edit['customer'][0]
    DB_SESSION.commit()
