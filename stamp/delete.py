def delete_workday_or_tag(db, id, tag_id=None):
    if not tag_id:
        db_query = db.get('Workday', id)
    else:
        db_query = db.get('Tag', id)
    db.delete(db_query)
