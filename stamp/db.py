import os
import sys

from sqlalchemy import exc, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import exc as orm_exc

from .mappings import Workday, Customer, Base, Invoice, Project, Tag
from .exceptions import (NoMatchingDatabaseEntryError,
                         TooManyMatchingDatabaseEntriesError,
                         CurrentStampNotFoundError, NonExistingId)
from .settings import DATA_DIR
from .formatting import yes_or_no

__all__ = ['Database']

class Database():
    def __init__(self, db_file, ask=True):
        self.engine = create_engine('sqlite:///' + db_file)
        if os.path.isfile(db_file):
            self.new_db = False
            Base.metadata.create_all(self.engine)
        else:
            self.new_db = True
            if ask:
                yes_or_no('Do you wish to create a new database called %s?' % db_file.split('/')[-1].split('.')[0],
                          no_message='Canceled...',
                          no_function=sys.exit,
                          no_function_args=(0,),
                          yes_message='Creating database!')
            try:
                Base.metadata.create_all(self.engine)
            except exc.OperationalError as err:
                if not os.path.exists(DATA_DIR):
                    os.makedirs(DATA_DIR)
                    Base.metadata.create_all(self.engine)
                else:
                    raise err
        session = sessionmaker(bind=self.engine)
        self.session = session()

    def add(self, instance):
        self.session.add(instance)
        # Creates the id which is necessary when connecting instances
        self.session.flush()

    def delete(self, instance):
        self.session.delete(instance)

    def reset(self):
        try:
            self.session.expunge()
        except TypeError:
            pass
        if self.new_db:
            os.remove(self.engine.url.database)

    def commit(self):
        self.session.commit()

    def resolve_table_name(self, table_name):
        try:
            table = eval(table_name.capitalize()) # NOQA
        except TypeError:
            raise NoMatchingDatabaseEntryError('Table was not found!')
        return table

    def get(self, table_name, id=None):
        table = self.resolve_table_name(table_name)
        if id:
            query = self.session.query(table).get(id)
            if not query:
                raise NonExistingId('%s with %s as id does not exist!' % (table_name.capitalize(), id))
        else:
            query = self.session.query(table)
            if not query.count():
                raise NoMatchingDatabaseEntryError('No %ss created yet!' % table_name.lower())

        return query

    def current_stamp(self):
        stamp = self.session.query(Workday).filter_by(end=None).first()
        if stamp:
            return stamp
        else:
            raise CurrentStampNotFoundError('Not stamped in!')

    def query_db_export_filter(self, table_name, export_filter):
        query = self.get(table_name)
        for key, value in export_filter.items():
            query = query.filter(value['op_func'](getattr(table_name, key), value['value']))
        if query.count() == 0:
            raise NoMatchingDatabaseEntryError('No matching database entry found with search string: %s' % value['value'])
        else:
            return query

    def get_last_workday_entry(self, *args):
        query = self.session.query(Workday).order_by(Workday.id).first()
        if not query:
            raise NoMatchingDatabaseEntryError('No matching database entry found with args: %s' % '.'.join(args))
        else:
            for attr in args:
                query = getattr(query, attr)
            return query

    def get_related_invoice(self, year, month):
        invoices = self.get('Invoice').filter(Invoice.month == month,
                                              Invoice.year == year).order_by(
                                                  Invoice.id.desc())
        if invoices.count() == 0:
            raise NoMatchingDatabaseEntryError('No invoice found for %s %s!' % (month, year))
        else:
            return invoices.first()

    def get_workdays(self, object_id, customer=None, invoice_id=None):
        # Used with delete or edit argument
        if object_id:
            workdays = self.session.query(Workday).get(object_id)
            if not workdays:
                raise NoMatchingDatabaseEntryError('Specified id not found!')

        # Used with status or export argument
        else:
            try:
                # Excluding current stamp
                workdays = self.session.query(Workday).filter(Workday.end.isnot(None)).order_by(Workday.start)
                # Query with filter
                if customer:
                    workdays = workdays.filter(Customer.name == customer)
                if invoice_id:
                    workdays = workdays.filter(Workday.invoice_id == invoice_id)
                if not workdays.count():
                    raise NoMatchingDatabaseEntryError('No workday has been completed yet!')
            except orm_exc.UnmappedInstanceError:
                raise NoMatchingDatabaseEntryError('Specified id not found!')
        return workdays

    def get_project(self, project_name):
        project = self.get('Project').filter(Project.name == project_name)
        if project.count() == 0:
            raise NoMatchingDatabaseEntryError('No matching project found for %s!' % project_name)
        elif project.count() > 1:
            raise TooManyMatchingDatabaseEntriesError('Several projects matches this string: %s!' % project_name)
        else:
            return project.first()
