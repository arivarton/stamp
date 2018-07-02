import os
import sys
import unittest
from unittest.mock import patch
from io import StringIO
from shutil import rmtree
from datetime import datetime, timedelta
from random import randrange as rrange
from calendar import monthrange

sys.path.append('../stamp')

from stamp import stamp, settings # NOQA

testing_db = 'test'
testing_db_path = os.path.join(settings.DATA_DIR, testing_db) + '.db'


# [TODO] Need to patch properly for stdin
class TestStampCLI(unittest.TestCase):

    def test_completing_workday_with_tags(self):
        # Create workday with current time
        with patch('sys.stdin.read', return_value='y'), patch('builtins.input', lambda: 'test value'):
            parser = stamp.parse_args(['in', '-c', 'test_company', '-p',
                                       'test_project', '--db', testing_db])
            self.assertTrue(parser.func(parser))
        parser = stamp.parse_args(['tag', 'testing tag', '--db', testing_db])
        self.assertTrue(parser.func(parser))
        parser = stamp.parse_args(['tag', 'testing tag 2', '--db', testing_db])
        self.assertTrue(parser.func(parser))
        parser = stamp.parse_args(['out', '--db', testing_db])
        self.assertTrue(parser.func(parser))

        # Create another workday with random date
        random_year = rrange(1900, 2200)
        random_month = rrange(1, 13)
        random_day = rrange(1, monthrange(random_year, random_month)[1] + 1)
        random_datetime = datetime(year=random_year,
                                   month=random_month,
                                   day=random_day,
                                   hour=rrange(0, 24),
                                   minute=rrange(0, 60))
        parser = stamp.parse_args(['in', '-c', 'test_company', '-p', 'test_project',
                                   '-D', '{:%x}'.format(random_datetime),
                                   '-T', '{:%H:%M}'.format(random_datetime),
                                   '--db', testing_db])
        self.assertTrue(parser.func(parser))
        parser = stamp.parse_args(['tag', 'testing tag',
                                   '-D', '{:%x}'.format(random_datetime),
                                   '-T', '{:%H:%M}'.format(random_datetime),
                                   '--db', testing_db])
        self.assertTrue(parser.func(parser))
        parser = stamp.parse_args(['tag', 'testing tag 2',
                                   '-D', '{:%x}'.format(random_datetime + timedelta(hours=3)),
                                   '-T', '{:%H:%M}'.format(random_datetime + timedelta(hours=3)),
                                   '--db', testing_db])
        self.assertTrue(parser.func(parser))
        parser = stamp.parse_args(['out',
                                   '-D', '{:%x}'.format(random_datetime + timedelta(hours=6)),
                                   '-T', '{:%H:%M}'.format(random_datetime + timedelta(hours=6)),
                                   '--db', testing_db])
        self.assertTrue(parser.func(parser))

        # Get status of database
        parser = stamp.parse_args(['status', '--db', testing_db])
        self.assertTrue(parser.func(parser))


def tearDownModule():
    if os.path.isfile(testing_db_path):
        os.remove(testing_db_path)


if __name__ == '__main__':
    unittest.main()
