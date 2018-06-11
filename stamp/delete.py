def delete_workday_or_tag(workday_id, tag_id, db):
    workday = db.query_for_workdays(workday_id, tag_id)
    db.session.delete(workday)
    db.session.commit()
