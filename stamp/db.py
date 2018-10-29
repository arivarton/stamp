import os
import sys

from sqlalchemy import exc, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import exc as orm_exc

from .mappings import Workday, Customer, Base, Invoice, Project # NOQA
from .exceptions import (NoMatchingDatabaseEntryError,
                         TooManyMatchingDatabaseEntriesError,
                         CurrentStampNotFoundError)
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

    def query_for_workdays(self, args):
        # Used with delete or edit argument
        if args.id:
            workdays = self.session.query(Workday).get(args.id)
            if not workdays:
                raise NoMatchingDatabaseEntryError('Specified id not found!')

        # Used with status or export argument
        else:
            try:
                # Excluding current stamp
                workdays = self.session.query(Workday).filter(Workday.end.isnot(None)).order_by(Workday.start)
                # Query with filter
                if hasattr(args, 'customer') and args.customer:
                    workdays = workdays.filter(Customer.name==args.customer)
                if hasattr(args, 'invoice_id') and args.invoice_id:
                    workdays = workdays.filter(Workday.invoice_id==args.invoice_id)
                if not workdays.count():
                    raise NoMatchingDatabaseEntryError('No workday has been completed yet!')
            except orm_exc.UnmappedInstanceError:
                raise NoMatchingDatabaseEntryError('Specified id not found!')
        return workdays

    def query_for_customer(self, id):
        customer = self.session.query(Customer).get(id)
        if customer:
            return customer
        else:
            raise NoMatchingDatabaseEntryError('No db entries matching id %s' % id)

    def query_for_project(self, id):
        project = self.session.query(Project).get(id)
        if project:
            return project
        else:
            raise NoMatchingDatabaseEntryError('No db entries matching id %s' % id)

    def current_stamp(self):
        try:
            stamp = self.session.query(Workday).filter(Workday.end.is_(None))[0]
        except IndexError:
            raise CurrentStampNotFoundError('Not stamped in!')
        return stamp

    def query_db_all(self, Table):
        table = eval(Table) # NOQA
        query = self.session.query(table)
        if query.count():
            return query
        else:
            raise NoMatchingDatabaseEntryError('No database entries in %s table!' % Table)

    def query_db_export_filter(self, Table, export_filter):
        table = eval(Table) # NOQA
        query = self.session.query(table)
        for key, value in export_filter.items():
            query = query.filter(value['op_func'](getattr(table, key), value['value']))
            if not query.count():
                raise NoMatchingDatabaseEntryError('No matching database entry found with search string: %s' % value['value'])

        return query

    def query_db(self, Table, column_name, search_string):
        try:
            table = eval(Table) # NOQA
        except TypeError:
            raise NoMatchingDatabaseEntryError('Table was not found.')
        db_filter = getattr(table, column_name)
        db_filter = db_filter.is_(search_string)

        return self.session.query(table).filter(db_filter)

    def get_one_db_entry(self, Table, column_name, search_string):
        query = self.query_db(Table, column_name, search_string)

        if query.count() == 1:
            return query.first()
        elif query.count() > 1:
            raise TooManyMatchingDatabaseEntriesError('Several database entries found matching', search_string + '!\n' + 'Canceling...')
        else:
            raise NoMatchingDatabaseEntryError('No matching database entry found with search string: %s' % search_string)

    def get_last_workday_entry(self, *args):
        query = self.session.query(Workday).order_by(Workday.id).first()
        if not query:
            raise NoMatchingDatabaseEntryError('No matching database entry found with args: %s' % '.'.join(args))
        else:
            for attr in args:
                query = getattr(query, attr)
            return query

    def get_invoices(self, args):
        try:
            invoices = self.query_db_all('Invoice')
            if args.id:
                invoices = invoices.filter(Invoice.id==args.id)
        except NoMatchingDatabaseEntryError:
            raise NoMatchingDatabaseEntryError('No invoices created yet! See help for export command to create one.')
        if not args.show_superseeded:
            # order_by is set only because of a stackoverflow comment. Haven't
            # tested if it's necessary.
            # https://stackoverflow.com/questions/1370997/group-by-year-month-day-in-a-sqlalchemy
            invoices = invoices.order_by(Invoice.month).group_by(Invoice.month)
        return invoices

    def get_related_invoice(self, year, month):
        query = self.session.query(Invoice).filter(Invoice.month == month,
                                                   Invoice.year == year).order_by(
                                                       Invoice.id.desc())
        if query.count() == 0:
            raise NoMatchingDatabaseEntryError('No invoice found for %s %s!' % (month, year))
        else:
            return query.first()
