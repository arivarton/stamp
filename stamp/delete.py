from .exceptions import DeleteNotAllowedError

__all__ = ['delete_workday_or_tag']

def delete_workday_or_tag(db, id, tag_id=None, force=False):
    if not tag_id:
        db_query = db.get('Workday', id)
        invoice_id = db_query.invoice_id
    else:
        db_query = db.get('Tag', tag_id)
        invoice_id = db_query.workday.invoice_id
    if invoice_id and not force:
        raise DeleteNotAllowedError('Unable to delete since this object has been\
                                    assigned an invoice id!')
    else:
        return db.delete(db_query)
