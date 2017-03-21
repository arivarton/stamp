#!/usr/bin/env python

##############################
#
#    Stamp in before starting
#    the workday, tag
#    points in time with
#    comments and stamp out
#    when workday is over.
#
##############################

from datetime import datetime
from . import __version__
import logging
import argparse
import pickle
import os

# Setup log file
FORMAT = logging.basicConfig(filename=".workhours.log",
                             filemode='a',
                             format='%(asctime)s %(levelname)s: %(message)s',
                             level=logging.DEBUG,
                             datefmt='%H:%M:%S')
logger = logging.getLogger('workhours')

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
STAMP_FILE = os.path.join(BASE_DIR, 'current_stamp.pickle')


def get_parser():
    parser = argparse.ArgumentParser(description='''Register work hours.
                                     Hours get automatically sorted by date and
                                     month is the default separator.''',
                                     epilog='''By arivarton
                                     (http://www.arivarton.com)''')
    parser.add_argument('-t', '--tag', type=str, default=False,
                        help='''Tag new or current (if already initalized)
                        stamp with a comment. Marked with current time or
                        time specified by the date argument.''')
    parser.add_argument('-d', '--datetime', type=str, default=datetime.now(),
                        help='Set date and time manually.')
    parser.add_argument('-h', '--hours', type=str, default='08:00-16:00',
                        help='Set hours.')
    parser.add_argument('-s', '--status', action='store_true',  # Finished
                        help='Print current state of stamp.')
    parser.add_argument('-e', '--export', type=str,
                        help='Export as PDF.', default=False)
    parser.add_argument('-v', '--version', action='store_true',  # Finished
                        help='Display current version.')
    return parser


def _write_pickle(stamp):
    pickle.dump(stamp, open(STAMP_FILE), 'wb')


def _create_stamp(args):
    stamp = _current_stamp()
    if stamp is not None and args['tag'] is False:
        stamp.update({'end': args['date']})
    elif args['tag']:
        stamp['tags'].update({id: {'comment': args['tag'], 'time': args['date']}})
    else:
        stamp = {'start': args['date'], 'tags': {}}
    _write_pickle(stamp)


def _current_stamp():
    if os.path.isfile(STAMP_FILE):
        stamp = pickle.open(STAMP_FILE, 'rb')
    else:
        stamp = None
    return stamp


def run():
    parser = get_parser()
    args = vars(parser.parse_args())

    if args['version']:
        print(__version__)
        return

    if args['status']:
        return  ### NEED TO PRINT THE STATUS HERE ###

    if args['export']:
        return  ### NEED TO EXPORT TO PDF HERE ###

    _create_stamp(args)

if __name__ == '__main__':
    run()
