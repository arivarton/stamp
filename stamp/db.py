import os

from sqlalchemy import exc, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import exc as orm_exc

from .mappings import Workday, Customer, Base
from .exceptions import (NoMatchingDatabaseEntryError,
                         TooManyMatchingDatabaseEntriesError,
                         CurrentStampNotFoundError)
from .settings import DATA_DIR


class Database():
    def __init__(self, db_file):
        engine = create_engine('sqlite:///' + db_file)
        try:
            Base.metadata.create_all(engine)
        except exc.OperationalError as err:
            if not os.path.exists(DATA_DIR):
                os.makedirs(DATA_DIR)
                Base.metadata.create_all(engine)
            else:
                raise err
        session = sessionmaker(bind=engine)
        self.session = session()

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
            # [TODO] Log that no matching database entries were found
            raise NoMatchingDatabaseEntryError('No matching database entry found with search string: %s' % search_string)

    def get_last_workday_entry(self, *args):
        query = self.session.query(Workday).order_by(Workday.id).first()
        if not query:
            raise NoMatchingDatabaseEntryError('No matching database entry found with args: %s' % '.'.join(args))
        else:
            for attr in args:
                query = getattr(query, attr)
            return query
