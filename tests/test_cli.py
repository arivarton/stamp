import os
import sys
import unittest
import lorem
from unittest.mock import patch
from uuid import uuid4
from shutil import rmtree
from datetime import datetime, timedelta
from random import randrange as rrange
from calendar import monthrange

sys.path.append('../stamp')

from stamp import args, settings # NOQA

testing_db = 'test_%s' % uuid4().hex
testing_db_path = os.path.join(settings.DATA_DIR, testing_db) + '.db'
customer_name = 'Test Company AS'
project_name = 'Test Project'


# [TODO] Need to patch properly for stdin
class TestStampCLI(unittest.TestCase):

    def test_completing_workday_with_tags(self):
        # Create workday with current time
        with patch('sys.stdin.read', return_value='y'), patch('builtins.input', lambda: 'test value'):
            print('Stamping in.')
            parser = args.parse(['in', '-c', customer_name, '-p',
                                 project_name, '--db', testing_db])
            self.assertTrue(parser.func(parser))
        print('Tagging.')
        parser = args.parse(['tag', 'testing tag', '--db', testing_db])
        self.assertTrue(parser.func(parser))
        print('Tagging.')
        parser = args.parse(['tag', '%s' % lorem.paragraph(), '--db', testing_db])
        self.assertTrue(parser.func(parser))
        out_time = datetime.now() + timedelta(hours=3)
        parser = args.parse(['out',
                             '-D', '{:%x}'.format(out_time),
                             '-T', '{:%H:%M}'.format(out_time),
                             '--db', testing_db])
        self.assertTrue(parser.func(parser))

        # Add another workday with current time one day later
        current_time = datetime.now() + timedelta(days=1)
        with patch('sys.stdin.read', return_value='y'), patch('builtins.input', lambda: 'test value'):
            parser = args.parse(['in', '-c', customer_name, '-p',
                                 project_name,
                                 '-D', '{:%x}'.format(current_time),
                                 '-T', '{:%H:%M}'.format(current_time),
                                 '--db', testing_db])
            self.assertTrue(parser.func(parser))
        parser = args.parse(['tag', 'testing tag',
                             '-D', '{:%x}'.format(current_time + timedelta(hours=1)),
                             '-T', '{:%H:%M}'.format(current_time + timedelta(hours=1)),
                             '--db', testing_db])
        self.assertTrue(parser.func(parser))
        parser = args.parse(['tag', '%s' % lorem.paragraph(),
                             '-D', '{:%x}'.format(current_time + timedelta(hours=2)),
                             '-T', '{:%H:%M}'.format(current_time + timedelta(hours=2)),
                             '--db', testing_db])
        self.assertTrue(parser.func(parser))
        out_time = current_time + timedelta(hours=3)
        parser = args.parse(['out',
                             '-D', '{:%x}'.format(out_time),
                             '-T', '{:%H:%M}'.format(out_time),
                             '--db', testing_db])
        self.assertTrue(parser.func(parser))

        # Add another workday with current time one day before
        current_time = datetime.now() + timedelta(days=-1)
        with patch('sys.stdin.read', return_value='y'), patch('builtins.input', lambda: 'test value'):
            parser = args.parse(['in', '-c', customer_name, '-p',
                                 project_name,
                                 '-D', '{:%x}'.format(current_time),
                                 '-T', '{:%H:%M}'.format(current_time),
                                 '--db', testing_db])
            self.assertTrue(parser.func(parser))
        parser = args.parse(['tag', 'testing tag',
                             '-D', '{:%x}'.format(current_time + timedelta(hours=1)),
                             '-T', '{:%H:%M}'.format(current_time + timedelta(hours=1)),
                             '--db', testing_db])
        self.assertTrue(parser.func(parser))
        parser = args.parse(['tag', '%s' % lorem.paragraph(),
                             '-D', '{:%x}'.format(current_time + timedelta(hours=2)),
                             '-T', '{:%H:%M}'.format(current_time + timedelta(hours=2)),
                             '--db', testing_db])
        self.assertTrue(parser.func(parser))
        out_time = current_time + timedelta(hours=3)
        parser = args.parse(['out',
                             '-D', '{:%x}'.format(out_time),
                             '-T', '{:%H:%M}'.format(out_time),
                             '--db', testing_db])
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
        parser = args.parse(['in', '-c', customer_name, '-p', project_name,
                             '-D', '{:%x}'.format(random_datetime),
                             '-T', '{:%H:%M}'.format(random_datetime),
                             '--db', testing_db])
        self.assertTrue(parser.func(parser))
        parser = args.parse(['tag', 'testing tag',
                             '-D', '{:%x}'.format(random_datetime),
                             '-T', '{:%H:%M}'.format(random_datetime),
                             '--db', testing_db])
        self.assertTrue(parser.func(parser))
        parser = args.parse(['tag', '%s' % lorem.paragraph(),
                             '-D', '{:%x}'.format(random_datetime + timedelta(hours=3)),
                             '-T', '{:%H:%M}'.format(random_datetime + timedelta(hours=3)),
                             '--db', testing_db])
        self.assertTrue(parser.func(parser))
        parser = args.parse(['out',
                             '-D', '{:%x}'.format(random_datetime + timedelta(hours=6)),
                             '-T', '{:%H:%M}'.format(random_datetime + timedelta(hours=6)),
                             '--db', testing_db])
        self.assertTrue(parser.func(parser))

        # Get status of database
        parser = args.parse(['status', 'workdays', '--db', testing_db])
        self.assertTrue(parser.func(parser))

        # Export invoice with current time workdays to pdf and open with default
        # viewer
        with patch('sys.stdin.read', return_value='y'):
            parser = args.parse(['export', '{:%B}'.format(datetime.now()),
                                 '{:%Y}'.format(datetime.now()),
                                 customer_name,
                                 '--pdf', '--db', testing_db])
            current_pdf = parser.func(parser)
            self.assertTrue(current_pdf)
            os.system('xdg-open ' + '\'%s\'' % current_pdf)


def tearDownModule():
    if os.path.isfile(testing_db_path):
        os.remove(testing_db_path)
    invoice_folder = os.path.join(settings.INVOICE_DIR, testing_db)
    if os.path.isdir(invoice_folder):
        rmtree(invoice_folder)


if __name__ == '__main__':
    unittest.main()
