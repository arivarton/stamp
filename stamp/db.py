import os
import sys

from sqlalchemy import exc, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import exc as orm_exc

from .mappings import Workday, Customer, Base, Invoice, Project # NOQA
from .exceptions import (NoMatchingDatabaseEntryError,
                         TooManyMatchingDatabaseEntriesError,
                         CurrentStampNotFoundError, NonExistingId)
from .settings import DATA_DIR
from .formatting import yes_or_no




class Database():
    def __init__(self, db_file):
        self.engine = create_engine('sqlite:///' + db_file)
        if os.path.isfile(db_file):
            self.new_db = False
            Base.metadata.create_all(self.engine)
        else:
            self.new_db = True
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
        try:
            if id:
                query = self.session.query(table).get(id)
            else:
                query = self.session.query(table)
        except NoMatchingDatabaseEntryError:
            raise NoMatchingDatabaseEntryError('No %ss created yet!' % table_name.lower())
        if not query:
            raise NonExistingID('%s with %s as id does not exist!' % (table_name.capitalize(), id))
        else:
            return query

    def current_stamp(self):
        try:
            stamp = self.session.query(Workday).filter(Workday.end.is_(None))[0]
        except IndexError:
            raise CurrentStampNotFoundError('Not stamped in!')
        return stamp

    def query_db_export_filter(self, table_name, export_filter):
        query = self.get(table_name)
        for key, value in export_filter.items():
            query = query.filter(value['op_func'](getattr(table, key), value['value']))
        if query.count() == 0:
            raise NoMatchingDatabaseEntryError('No matching database entry found with search string: %s' % value['value'])
        else:
            return query

    def get_with_filter(self, table_name, column_name, search_string):
        table = self.resolve_table_name(table_name)
        query = self.get(table_name)
        db_filter = getattr(table, column_name).is_(search_string)
        query.filter(db_filter)

        if query.count() == 0:
            raise NoMatchingDatabaseEntryError('No matching database entry found with search string: %s' % search_string)
        else:
            return query.all()

    def get_last_workday_entry(self, *args):
        query = self.session.query(Workday).order_by(Workday.id).first()
        if not query:
            raise NoMatchingDatabaseEntryError('No matching database entry found with args: %s' % '.'.join(args))
        else:
            for attr in args:
                query = getattr(query, attr)
            return query

    def get_related_invoice(self, year, month):
        invoices = self.get('Invoice', id)
        invoices.filter(Invoice.month == month,
                        Invoice.year == year).order_by(
                        Invoice.id.desc())
        if invoices.count() == 0:
            raise NoMatchingDatabaseEntryError('No invoice found for %s %s!' % (month, year))
        else:
            return invoices.first()

    def query_for_workdays(self, id, customer=None, invoice_id=None):
        # Used with delete or edit argument
        if id:
            workdays = self.session.query(Workday).get(id)
            if not workdays:
                raise NoMatchingDatabaseEntryError('Specified id not found!')

        # Used with status or export argument
        else:
            try:
                # Excluding current stamp
                workdays = self.session.query(Workday).filter(Workday.end.isnot(None)).order_by(Workday.start)
                # Query with filter
                if customer:
                    workdays = workdays.filter(Customer.name==customer)
                if invoice_id:
                    workdays = workdays.filter(Workday.invoice_id==invoice_id)
                if not workdays.count():
                    raise NoMatchingDatabaseEntryError('No workday has been completed yet!')
            except orm_exc.UnmappedInstanceError:
                raise NoMatchingDatabaseEntryError('Specified id not found!')
        return workdays
