# Stamp introduction

Register work hours in cli (Curses interface is under development).

Stamp in before starting the workday, tag points in time with comments and stamp out when workday is over.

Hours are saved to a sqlite database and exportable to pdf.

PDF is currently in Norwegian, needs to be translated.


# Environment variables

See stamp/settings.py.


# Install

`python3 setup.py install`


# Usage

Run `stamp --help`


# Config file

Not implemented yet. See stamp/config.py.


# Development FAQ

Look in stamp/main.py to get a quick overview.

When changing code for mappings, any old databases will be uncompatible with the changes. A manuall fix by entering the hours again to a new database will be required.


# Disclaimer

This software is still in alpha and is therefore not recommended for daily usage as any changes of versions can make the old database unreadable.
