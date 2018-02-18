from __init__ import DB_SESSION
from db import query_for_workdays


def delete_workday_or_tag(workday_id, tag_id):
    objects = query_for_workdays(workday_id, tag_id)
    for workday in objects:
        DB_SESSION.delete(workday)
    DB_SESSION.commit()
