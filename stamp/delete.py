def delete_workday_or_tag(db, args):
    workday = db.query_for_workdays(args)
    db.delete(workday)
