import sys
import argparse
from datetime import datetime

__all__ = ['DateAction',
           'TimeAction',
           'IdAction']

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
                 help='Choose id. Default is current.',
                 required=False,
                 default='current'):
        super(IdAction, self).__init__(option_strings,
                                         dest,
                                         help=help,
                                         required=required,
                                         default=default)

    def __call__(self, parser, namespace, values, option_string=None):
        if self.values == 'current':
            setattr(namespace, self.dest, self.values)
        else:
            try:
                setattr(namespace, self.dest, int(self.values))
            except ValueError:
                print('Invalid id!\nId must consist of a valid integer or contain the keyword\'current\'')
                sys.exit(0)
