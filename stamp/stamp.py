#!/usr/bin/env python3

import sys
from .args import parse


def run():
    parser = parse(sys.argv[1:])
    if vars(parser):
        parser.func(parser)
    else:
        parser.print_help()


if __name__ == '__main__':
    run()
