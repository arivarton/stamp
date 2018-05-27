from . import DB_SESSION
from .db import query_for_workdays


def delete_workday_or_tag(workday_id, tag_id):
    workday = query_for_workdays(workday_id, tag_id)
    DB_SESSION.delete(workday)
    DB_SESSION.commit()
