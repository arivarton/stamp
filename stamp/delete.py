def delete_workday_or_tag(db, workday_id, tag_id):
    workday = db.query_for_workdays(workday_id, tag_id)
    db.delete(workday)
