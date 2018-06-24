import sys
import argparse
from datetime import datetime


class DateAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        try:
            setattr(namespace, self.dest, datetime.strptime(values, '%x').date())
        except ValueError:
            print('According to system locale, date should be in this format: %s!' % datetime.today().strftime('%x'))
            sys.exit(0)
