#!/usr/bin/env python3

import sys
import curses
from .args import parse
from .ui.main import main as curses_interface
from .exceptions import RequiredValueError
from .helpers import error_handler


def run():
    parser = parse(sys.argv[1:])

    # Validate values in args
    for attr_name in parser.__dict__:
        attr = parser.__dict__[attr_name]
        if hasattr(attr, 'validate'):
            try:
                attr.validate()
            except RequiredValueError as err_msg:
                error_handler(err_msg)

    if vars(parser):
        parser.func(parser)
    else:
        curses.wrapper(curses_interface)


if __name__ == '__main__':
    run()
