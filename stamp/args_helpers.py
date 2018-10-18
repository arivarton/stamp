import os
import sys
import argparse
from datetime import datetime

from .db import Database
from .settings import DATA_DIR, DB_FILE
from .decorators import no_db_no_action_decorator
from .exceptions import CurrentStampNotFoundError, RequiredValueError

__all__ = ['DateAction',
           'TimeAction',
           'IdAction',
           'DbAction',
           'FromEnvAction']

class DateAction(argparse.Action):
    date_format = '%x'

    def __init__(self,
                 option_strings,
                 dest,
                 help='Set date manually. With current date on this systems locale settings the format is: \'%s\'. Default date is now!' % datetime.today().strftime(date_format), # NOQA
                 type=str, # NOQA
                 required=False,
                 default=datetime.now().date()):
        super(DateAction, self).__init__(option_strings=option_strings,
                                         dest=dest,
                                         help=help,
                                         type=type,
                                         required=required,
                                         default=default)

    def __call__(self, parser, namespace, values, option_string=None):
        try:
            setattr(namespace, self.dest, datetime.strptime(values, self.date_format).date())
        except ValueError:
            print('Incorrect date format!\nAccording to system locale, date should be in this format: %s' % datetime.today().strftime(self.date_format))
            sys.exit(0)


class TimeAction(argparse.Action):
    time_format = '%H:%M'

    def __init__(self,
                 option_strings,
                 dest,
                 help='Set time manually. With current time the format is \'%s\'. Default is time now!' % datetime.today().strftime(time_format), # NOQA
                 type=str, # NOQA
                 required=False,
                 default=datetime.now().time().replace(second=0, microsecond=0)):
        super(TimeAction, self).__init__(option_strings,
                                         dest,
                                         help=help,
                                         type=type,
                                         required=required,
                                         default=default)

    def __call__(self, parser, namespace, values, option_string=None):
        try:
            setattr(namespace, self.dest, datetime.strptime(values, '%H:%M').time())
        except ValueError:
            print('Incorrect time format!\nExample of correct format for current time: %s' % datetime.today().strftime('%H:%M'))
            sys.exit(0)


class IdAction(argparse.Action):
    def __init__(self,
                 option_strings,
                 dest,
                 help='Choose id.',
                 required=False,
                 nargs='?',
                 default=None):
        super(IdAction, self).__init__(option_strings,
                                       dest,
                                       help=help,
                                       required=required,
                                       nargs=nargs,
                                       default=default)



    def __call__(self, parser, namespace, values, option_string=None):
        @no_db_no_action_decorator
        def get_db_object(namespace):
            called_from = namespace.parser_object.split(' ')[-1]
            if called_from == 'workdays':
                namespace.db_query = namespace.db.query_for_workdays(namespace)
            elif called_from == 'invoices':
                namespace.db_query = namespace.db.get_invoices(namespace)
        get_db_object(namespace)
        try:
            if values:
                setattr(namespace, self.dest, int(values))
        except ValueError:
            print('Invalid id!\nId must only consist of integers.')
            sys.exit(0)


class DbAction(argparse.Action):
    def __init__(self,
                 option_strings,
                 dest,
                 help='Name of database.',
                 type=str, # NOQA
                 required=False,
                 default=Database(os.path.join(DATA_DIR, DB_FILE) + '.db')):
        super(DbAction, self).__init__(option_strings,
                                       dest,
                                       help=help,
                                       type=type,
                                       required=required,
                                       default=default)

    def __call__(self, parser, namespace, values, option_string=None):
        db_dir = os.path.join(DATA_DIR, values) + '.db'
        setattr(namespace, self.dest, Database(db_dir))


class FromEnvObject(object):
    def __init__(self, string, dest, option_strings, env_var):
        self.string = string
        self.dest = dest
        self.option_strings = option_strings
        self.env_var = env_var

    def __str__(self):
        return self.string

    def __repr__(self):
        return self.string

    def __add__(self, add):
        return self.string + add

    def __radd__(self, add):
        return add + self.string

    def validate(self):
        if not self.string:
            raise RequiredValueError('The %s value is required! It can be set via the %s parameter. Alternatively use the environment variable \'%s\'.' % (self.dest, ' or '.join(self.option_strings), self.env_var))




class FromEnvAction(argparse.Action):
    def __init__(self,
                 option_strings,
                 dest,
                 nargs=None,
                 env_var=None,
                 help=None,
                 type=str,
                 choices=None,
                 required=False,
                 default=None,
                 metavar=None):
        self.option_strings = option_strings
        self.dest = dest
        self.nargs = nargs
        self.env_var = env_var
        self.help = help
        self.type = type
        self.choices = choices
        self.required = required
        self.default = FromEnvObject(os.getenv(env_var), dest, option_strings, env_var)
        self.metavar = metavar

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, FromEnvObject(values, self.dest, self.option_strings, self.env_var))
