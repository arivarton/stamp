#!/usr/bin/env python3

import sys
import curses
from .args import parse
from .ui.main import main as curses_interface
from .exceptions import RequiredValueError
from .helpers import error_handler


def run():

    try:
        parser = parse(sys.argv[1:])
    except RequiredValueError as msg:
        error_handler(msg)
    if vars(parser):
        parser.func(parser)
    else:
        curses.wrapper(curses_interface)


if __name__ == '__main__':
    run()
