import os
import sys
import argparse
from datetime import datetime

from .constants import DATA_DIR, DB_FILE, CONFIG_DIR, CONFIG_FILE

__all__ = ['DateAction',
           'TimeAction',
           'DbAction',
           'FromEnvAction',
           'ConfigAction']

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


class DbAction(argparse.Action):
    def __init__(self,
                 option_strings,
                 dest,
                 help='Name of database.',
                 type=str, # NOQA
                 required=False,
                 default=os.path.join(DATA_DIR, DB_FILE) + '.db'):
        super(DbAction, self).__init__(option_strings,
                                       dest,
                                       help=help,
                                       type=type,
                                       required=required,
                                       default=default)

    def __call__(self, parser, namespace, values, option_string=None):
        db_dir = os.path.join(DATA_DIR, values) + '.db'
        setattr(namespace, self.dest, db_dir)


class ConfigAction(argparse.Action):
    def __init__(self,
                 option_strings,
                 dest,
                 help='Path to config file.',
                 type=str, # NOQA
                 required=False,
                 default=os.path.join(CONFIG_DIR, CONFIG_FILE)):
        super(ConfigAction, self).__init__(option_strings,
                                       dest,
                                       help=help,
                                       type=type,
                                       required=required,
                                       default=default)

    def __call__(self, parser, namespace, values, option_string=None):
        config_dir = os.path.expanduser(values)
        setattr(namespace, self.dest, config_dir)


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
        self.default = os.getenv(env_var)
        self.metavar = metavar

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)
