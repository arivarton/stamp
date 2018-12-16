# Stamp introduction
Register work hours in cli (Curses interface is under development).
Stamp in before starting the workday, tag points in time with comments and stamp out when workday is over.
Hours are saved to a sqlite database and exportable to pdf.
PDF is currently in Norwegian, needs to be translated.


# Environment variables

See stamp/settings.py.


# Install
## (Optional) Create virtual python environment
Download 'virtualenv'
`mkvirtualenv 'stamp-0.1.6'`
`workon 'stamp-0.1.6'`

## Download the "stable" version which is currently 0.1.6
`wget https://gitlab.com/arivarton/stamp/-/archive/0.1.6/stamp-0.1.6.tar.gz`
`tar -xvzf stamp-0.1.6.tar.gz`
`cd stamp-0.1.6`
`python3 setup.py install`


# Usage
Run `stamp --help`


# Config file
Not implemented yet. See stamp/config.py.


# Development FAQ
Look in stamp/main.py to get a quick overview.

When changing code for mappings, any old databases will be uncompatible with the changes. 
A manual fix by entering the hours again to a new database will be required.


# Disclaimer
This software is still in alpha and is therefore not recommended for daily usage as any changes of versions can make the old database unreadable.
