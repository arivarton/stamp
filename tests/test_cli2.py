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

from stamp import settings # NOQA
from stamp.db import Database
from stamp.add import stamp_in
from stamp.tag import tag_stamp
from stamp.end import stamp_out
from stamp.status import Status
from stamp.export import export_invoice
from stamp.delete import delete_workday_or_tag

testing_db = 'test_%s' % uuid4().hex
testing_db_path = os.path.join(settings.DATA_DIR, testing_db) + '.db'
with patch('sys.stdin.read', return_value='y'), patch('builtins.input', lambda: 'test value'):
    db = Database(testing_db_path)
customer_name = 'Test Company AS'
project_name = 'Test Project'


# [TODO] Need to patch properly for stdin
class TestStampCLI(unittest.TestCase):

    def test_completing_workday_with_tags(self):
        # Create workday with start time now
        date_and_time = datetime.now()
        # Stamp in
        with patch('sys.stdin.read', return_value='y'), patch('builtins.input', lambda: 'test value'):
            stamp = stamp_in(db, customer_name, project_name, date_and_time.date(),
                             date_and_time.time())
        self.assertTrue(stamp)
        # Tag with current time
        self.assertTrue(tag_stamp(db, date_and_time.date(), date_and_time.time(),
                                  stamp, lorem.paragraph()))
        # Tag with one added hour
        date_and_time = date_and_time + timedelta(hours=1)
        self.assertTrue(tag_stamp(db, date_and_time.date(), date_and_time.time(),
                                  stamp, lorem.paragraph()))
        # Tag with 3 added hours
        date_and_time = date_and_time + timedelta(hours=2)
        self.assertTrue(tag_stamp(db, date_and_time.date(), date_and_time.time(),
                                  stamp, lorem.paragraph()))
        # Stamp out
        self.assertTrue(stamp_out(db, date_and_time.date(), date_and_time.time()))

        # Create another workday a day later
        date_and_time = datetime.now() + timedelta(days=1)
        # Stamp in
        with patch('sys.stdin.read', return_value='y'), patch('builtins.input', lambda: 'test value'):
            stamp = stamp_in(db, customer_name, project_name, date_and_time.date(),
                             date_and_time.time())
        self.assertTrue(stamp)
        # Tag with current time
        self.assertTrue(tag_stamp(db, date_and_time.date(), date_and_time.time(),
                                  stamp, lorem.paragraph()))
        # Tag with 1 added hour
        date_and_time = date_and_time + timedelta(hours=1)
        self.assertTrue(tag_stamp(db, date_and_time.date(), date_and_time.time(),
                                  stamp, lorem.paragraph()))
        # Tag with 3 added hours
        date_and_time = date_and_time + timedelta(hours=2)
        self.assertTrue(tag_stamp(db, date_and_time.date(), date_and_time.time(),
                                  stamp, lorem.paragraph()))
        # Stamp out
        self.assertTrue(stamp_out(db, date_and_time.date(), date_and_time.time()))

        # Create another workday a day before
        date_and_time = datetime.now() + timedelta(days=-1)
        # Stamp in
        with patch('sys.stdin.read', return_value='y'), patch('builtins.input', lambda: 'test value'):
            stamp = stamp_in(db, customer_name, project_name, date_and_time.date(),
                             date_and_time.time())
        self.assertTrue(stamp)
        # Tag with current time
        self.assertTrue(tag_stamp(db, date_and_time.date(), date_and_time.time(),
                                  stamp, lorem.paragraph()))
        # Tag with 1 added hour
        date_and_time = date_and_time + timedelta(hours=1)
        self.assertTrue(tag_stamp(db, date_and_time.date(), date_and_time.time(),
                                  stamp, lorem.paragraph()))
        # Tag with 3 added hours
        date_and_time = date_and_time + timedelta(hours=2)
        self.assertTrue(tag_stamp(db, date_and_time.date(), date_and_time.time(),
                                  stamp, lorem.paragraph()))
        # Tag with 5 added hours
        date_and_time = date_and_time + timedelta(hours=2)
        self.assertTrue(tag_stamp(db, date_and_time.date(), date_and_time.time(),
                                  stamp, lorem.paragraph()))
        # Stamp out
        self.assertTrue(stamp_out(db, date_and_time.date(), date_and_time.time()))

        # Create another workday with random date
        random_year = rrange(1900, 2200)
        random_month = rrange(1, 13)
        random_day = rrange(1, monthrange(random_year, random_month)[1] + 1)
        date_and_time = datetime(year=random_year,
                                 month=random_month,
                                 day=random_day,
                                 hour=rrange(0, 24),
                                 minute=rrange(0, 60))
        # Stamp in
        with patch('sys.stdin.read', return_value='y'), patch('builtins.input', lambda: 'test value'):
            stamp = stamp_in(db, customer_name, project_name, date_and_time.date(),
                             date_and_time.time())
        self.assertTrue(stamp)
        # Tag with current time
        self.assertTrue(tag_stamp(db, date_and_time.date(), date_and_time.time(),
                                  stamp, lorem.paragraph()))
        # Tag with 1 added hour
        date_and_time = date_and_time + timedelta(hours=1)
        self.assertTrue(tag_stamp(db, date_and_time.date(), date_and_time.time(),
                                  stamp, lorem.paragraph()))
        # Tag with 3 added hours
        date_and_time = date_and_time + timedelta(hours=2)
        self.assertTrue(tag_stamp(db, date_and_time.date(), date_and_time.time(),
                                  stamp, lorem.paragraph()))
        # Tag with 5 added hours
        date_and_time = date_and_time + timedelta(hours=2)
        self.assertTrue(tag_stamp(db, date_and_time.date(), date_and_time.time(),
                                  stamp, lorem.paragraph()))
        # Stamp out
        self.assertTrue(stamp_out(db, date_and_time.date(), date_and_time.time()))

        # Create another workday a day later
        date_and_time = date_and_time + timedelta(days=1)
        # Stamp in
        with patch('sys.stdin.read', return_value='y'), patch('builtins.input', lambda: 'test value'):
            stamp = stamp_in(db, customer_name, project_name, date_and_time.date(),
                             date_and_time.time())
        self.assertTrue(stamp)
        # Tag with current time
        self.assertTrue(tag_stamp(db, date_and_time.date(), date_and_time.time(),
                                  stamp, lorem.paragraph()))
        # Tag with 1 added hour
        date_and_time = date_and_time + timedelta(hours=1)
        self.assertTrue(tag_stamp(db, date_and_time.date(), date_and_time.time(),
                                  stamp, lorem.paragraph()))
        # Tag with 3 added hours
        date_and_time = date_and_time + timedelta(hours=2)
        self.assertTrue(tag_stamp(db, date_and_time.date(), date_and_time.time(),
                                  stamp, lorem.paragraph()))
        # Stamp out
        self.assertTrue(stamp_out(db, date_and_time.date(), date_and_time.time()))

        # Create another workday a day before
        date_and_time = date_and_time + timedelta(days=-2)
        # Stamp in
        with patch('sys.stdin.read', return_value='y'), patch('builtins.input', lambda: 'test value'):
            stamp = stamp_in(db, customer_name, project_name, date_and_time.date(),
                             date_and_time.time())
        self.assertTrue(stamp)
        # Tag with current time
        self.assertTrue(tag_stamp(db, date_and_time.date(), date_and_time.time(),
                                  stamp, lorem.paragraph()))
        # Tag with 1 added hour
        date_and_time = date_and_time + timedelta(hours=1)
        self.assertTrue(tag_stamp(db, date_and_time.date(), date_and_time.time(),
                                  stamp, lorem.paragraph()))
        # Tag with 3 added hours
        date_and_time = date_and_time + timedelta(hours=2)
        self.assertTrue(tag_stamp(db, date_and_time.date(), date_and_time.time(),
                                  stamp, lorem.paragraph()))
        # Tag with 5 added hours
        date_and_time = date_and_time + timedelta(hours=2)
        self.assertTrue(tag_stamp(db, date_and_time.date(), date_and_time.time(),
                                  stamp, lorem.paragraph()))
        # Stamp out
        self.assertTrue(stamp_out(db, date_and_time.date(), date_and_time.time()))

        # Create another workday to test workday deletion
        # Stamp in
        with patch('sys.stdin.read', return_value='y'), patch('builtins.input', lambda: 'test value'):
            stamp = stamp_in(db, customer_name, project_name, date_and_time.date(),
                             date_and_time.time())
        self.assertTrue(stamp)
        # Tag with current time
        self.assertTrue(tag_stamp(db, date_and_time.date(), date_and_time.time(),
                                  stamp, 'This should be deleted.'))
        # Tag with 1 added hour
        date_and_time = date_and_time + timedelta(hours=1)
        self.assertTrue(tag_stamp(db, date_and_time.date(), date_and_time.time(),
                                  stamp, 'This should be deleted.'))
        # Tag with 3 added hours
        date_and_time = date_and_time + timedelta(hours=2)
        self.assertTrue(tag_stamp(db, date_and_time.date(), date_and_time.time(),
                                  stamp, 'This should be deleted.'))
        # Tag with 5 added hours
        date_and_time = date_and_time + timedelta(hours=2)
        self.assertTrue(tag_stamp(db, date_and_time.date(), date_and_time.time(),
                                  stamp, 'This should be deleted.'))
        # Stamp out
        self.assertTrue(stamp_out(db, date_and_time.date(), date_and_time.time()))
        # Delete
        delete_workday_or_tag(db, stamp.id)

        # Create another workday to test tag deletion
        date_and_time = datetime.now() + timedelta(days=10)
        # Stamp in
        with patch('sys.stdin.read', return_value='y'), patch('builtins.input', lambda: 'test value'):
            stamp = stamp_in(db, customer_name, project_name, date_and_time.date(),
                             date_and_time.time())
        self.assertTrue(stamp)
        # Tag with current time
        tag = tag_stamp(db, date_and_time.date(), date_and_time.time(),
                        stamp, 'This should be deleted.')
        self.assertTrue(tag)
        # Tag with 1 added hour
        date_and_time = date_and_time + timedelta(hours=1)
        self.assertTrue(tag_stamp(db, date_and_time.date(), date_and_time.time(),
                                  stamp, 'This should not be deleted.'))
        # Tag with 3 added hours
        date_and_time = date_and_time + timedelta(hours=2)
        self.assertTrue(tag_stamp(db, date_and_time.date(), date_and_time.time(),
                                  stamp, 'This should not be deleted.'))
        # Tag with 5 added hours
        date_and_time = date_and_time + timedelta(hours=2)
        self.assertTrue(tag_stamp(db, date_and_time.date(), date_and_time.time(),
                                  stamp, 'This should not be deleted.'))
        # Stamp out
        self.assertTrue(stamp_out(db, date_and_time.date(), date_and_time.time()))
        # Delete
        delete_workday_or_tag(db, stamp.id, tag.id)

        # Status of workdays
        status_object = Status(db.get('Workday', None))
        print(status_object)

        with patch('sys.stdin.read', return_value='y'):
            pdf = export_invoice(db, '{:%Y}'.format(datetime.now()),
                                '{:%B}'.format(datetime.now()), customer_name,
                                project_name, True)
        os.system('xdg-open ' + '\'%s\'' % pdf)



def tearDownModule():
    if os.path.isfile(testing_db_path):
        os.remove(testing_db_path)
    invoice_folder = os.path.join(settings.INVOICE_DIR, testing_db)
    if os.path.isdir(invoice_folder):
        rmtree(invoice_folder)


if __name__ == '__main__':
    unittest.main()
