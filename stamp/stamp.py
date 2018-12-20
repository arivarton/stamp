#!/usr/bin/env python3

import sys
import curses
from .args import parse
from .ui.main import main as curses_interface
from .db import Database
from .config import Config


def run(args=sys.argv[1:]):
    parser = parse(sys.argv[1:])
    parser.db = Database(parser.db)
    parser.config = Config(parser.config)

    if(parser.show_config):
        print(parser.config.values)
        sys.exit(0)

    if vars(parser):
        parser.func(parser)
    else:
        curses.wrapper(curses_interface)


if __name__ == '__main__':
    run()
