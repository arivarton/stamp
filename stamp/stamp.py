#!/usr/bin/env python3

import sys
import curses
from .args import parse
from .ui.main import main as curses_interface
from .exceptions import RequiredValueError
from .helpers import error_handler
from .db import Database


def run(args=sys.argv[1:]):
    parser = parse(sys.argv[1:])
    parser.db = Database(parser.db)

    if vars(parser):
        parser.func(parser)
    else:
        curses.wrapper(curses_interface)


if __name__ == '__main__':
    run()
