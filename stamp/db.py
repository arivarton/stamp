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


def create_database(db_file):
    engine = create_engine('sqlite:///' + db_file)
    try:
        Base.metadata.create_all(engine)
    except exc.OperationalError as err:
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
            Base.metadata.create_all(engine)
        else:
            raise err
    return engine


class Database():
    def __init__(self, db_file):
        if os.path.isfile(db_file):
            engine = create_database(db_file)
        else:
            engine = yes_or_no('Do you wish to create a new database called %s?' % db_file.split('/')[-1].split('.')[0],
                               no_message='Canceled...',
                               no_function=sys.exit,
                               no_function_args=(0,),
                               yes_message='Creating database!',
                               yes_function=create_database,
                               yes_function_args=(db_file,))
        session = sessionmaker(bind=engine)
        self.session = session()

    def add(self, instance):
        self.session.add(instance)
        # Creates the id which is necessary when connecting instances
        self.session.flush()

    def delete(self, instance):
        self.session.delete(instance)

    def commit(self):
        self.session.commit()

    def reset(self):
        self.session.expunge()

    def query_for_workdays(self, workday_id=None, tag_id=None, args=None):
        try:
            # Used with delete or edit argument
            if workday_id or tag_id:
                if tag_id:
                    #  workdays = self.session.query(Workday).get(workday_id).tags.filter(Tag.id_under_workday == tag_id)
                    raise NotImplementedError('Must figure out a way to match selected id with the actual tag id.')
                else:
                    workdays = self.session.query(Workday).get(workday_id)

            # Used with status or export argument
            else:
                # Query with filter
                if hasattr(args, 'filter') and args.filter:
                    if args.customer:
                        workdays = self.session.query(Customer).filter(Customer.name is args.customer).order_by(workdays.start)
                    elif args.time and args.date:
                        raise NotImplementedError('Filtering on time and date not implemented yet!')
                    elif args.date:
                        raise NotImplementedError('Filtering on date not implemented yet!')
                    elif args.time:
                        raise NotImplementedError('Filtering on time not implemented yet!')
                # Query for everything (excludes current stamp)
                else:
                    workdays = self.session.query(Workday).filter(Workday.end.isnot(None)).order_by(Workday.start)
        except orm_exc.UnmappedInstanceError:
            raise NoMatchingDatabaseEntryError('Specified id not found!')
        if not workdays.count():
            raise NoMatchingDatabaseEntryError('No workday has been completed yet!')
        return workdays

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
            raise TooManyMatchingDatabaseEntriesError('Several database entries found matching', search_string + '!\n' +
                                                      'Canceling...')
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

    def get_invoices(self, include_superseeded=False):
        try:
            invoices = self.query_db_all('Invoice')
        except NoMatchingDatabaseEntryError:
            raise NoMatchingDatabaseEntryError('No invoices created yet! See help for export command to create one.')
        if not include_superseeded:
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
