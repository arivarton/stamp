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

from stamp.constants import DATA_DIR, INVOICE_DIR # NOQA
from stamp.db import Database
from stamp.add import new_stamp
from stamp.tag import tag_stamp
from stamp.end import end_stamp
from stamp.status import Status
from stamp.export import export_invoice
from stamp.delete import delete_workday_or_tag
from stamp.config import Config

TESTING_DB = 'test_%s' % uuid4().hex
TESTING_DB_PATH = os.path.join(DATA_DIR, TESTING_DB) + '.db'
DB = Database(TESTING_DB_PATH, ask=False)
CUSTOMER_NAME = 'Test Company AS'
PROJECT_NAME = 'Test Project'

CONFIG = Config(None)


# [TODO] Need to patch properly for stdin
class TestStampCLI(unittest.TestCase):

    def test_completing_workday_with_tags(self):
        # Create workday with start time now
        date_and_time = datetime.now()
        # Stamp in
        stamp = new_stamp(DB, CUSTOMER_NAME, PROJECT_NAME, date_and_time.date(),
                          date_and_time.time(), ask=False)
        self.assertTrue(stamp)
        # Tag with current time
        self.assertTrue(tag_stamp(DB, date_and_time.date(), date_and_time.time(),
                                  stamp, lorem.paragraph()))
        # Tag with one added hour
        date_and_time = date_and_time + timedelta(hours=1)
        self.assertTrue(tag_stamp(DB, date_and_time.date(), date_and_time.time(),
                                  stamp, lorem.paragraph()))
        # Tag with 3 added hours
        date_and_time = date_and_time + timedelta(hours=2)
        self.assertTrue(tag_stamp(DB, date_and_time.date(), date_and_time.time(),
                                  stamp, lorem.paragraph()))
        # Stamp out
        self.assertTrue(end_stamp(DB, date_and_time.date(), date_and_time.time()))

        # Create another workday a day later
        date_and_time = datetime.now() + timedelta(days=1)
        # Stamp in
        stamp = new_stamp(DB, CUSTOMER_NAME, PROJECT_NAME, date_and_time.date(),
                         date_and_time.time(), ask=False)
        self.assertTrue(stamp)
        # Tag with current time
        self.assertTrue(tag_stamp(DB, date_and_time.date(), date_and_time.time(),
                                  stamp, lorem.paragraph()))
        # Tag with 1 added hour
        date_and_time = date_and_time + timedelta(hours=1)
        self.assertTrue(tag_stamp(DB, date_and_time.date(), date_and_time.time(),
                                  stamp, lorem.paragraph()))
        # Tag with 3 added hours
        date_and_time = date_and_time + timedelta(hours=2)
        self.assertTrue(tag_stamp(DB, date_and_time.date(), date_and_time.time(),
                                  stamp, lorem.paragraph()))
        # Stamp out
        self.assertTrue(end_stamp(DB, date_and_time.date(), date_and_time.time()))

        # Create another workday a day before
        date_and_time = datetime.now() + timedelta(days=-1)
        # Stamp in
        stamp = new_stamp(DB, CUSTOMER_NAME, PROJECT_NAME, date_and_time.date(),
                         date_and_time.time(), ask=False)
        self.assertTrue(stamp)
        # Print current stamp
        status_object = Status(DB.get('Workday', None), CONFIG)
        status_object.print_current_stamp(DB.current_stamp())
        # Tag with current time
        self.assertTrue(tag_stamp(DB, date_and_time.date(), date_and_time.time(),
                                  stamp, lorem.paragraph()))
        # Tag with 1 added hour
        date_and_time = date_and_time + timedelta(hours=1)
        self.assertTrue(tag_stamp(DB, date_and_time.date(), date_and_time.time(),
                                  stamp, lorem.paragraph()))
        # Tag with 3 added hours
        date_and_time = date_and_time + timedelta(hours=2)
        self.assertTrue(tag_stamp(DB, date_and_time.date(), date_and_time.time(),
                                  stamp, lorem.paragraph()))
        # Tag with 5 added hours
        date_and_time = date_and_time + timedelta(hours=2)
        self.assertTrue(tag_stamp(DB, date_and_time.date(), date_and_time.time(),
                                  stamp, lorem.paragraph()))
        # Print current stamp with tags
        status_object = Status(DB.get('Workday', None), CONFIG)
        status_object.print_current_stamp(DB.current_stamp())
        # Stamp out
        self.assertTrue(end_stamp(DB, date_and_time.date(), date_and_time.time()))

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
        stamp = new_stamp(DB, CUSTOMER_NAME, PROJECT_NAME, date_and_time.date(),
                         date_and_time.time(), ask=False)
        self.assertTrue(stamp)
        # Tag with current time
        self.assertTrue(tag_stamp(DB, date_and_time.date(), date_and_time.time(),
                                  stamp, lorem.paragraph()))
        # Tag with 1 added hour
        date_and_time = date_and_time + timedelta(hours=1)
        self.assertTrue(tag_stamp(DB, date_and_time.date(), date_and_time.time(),
                                  stamp, lorem.paragraph()))
        # Tag with 3 added hours
        date_and_time = date_and_time + timedelta(hours=2)
        self.assertTrue(tag_stamp(DB, date_and_time.date(), date_and_time.time(),
                                  stamp, lorem.paragraph()))
        # Tag with 5 added hours
        date_and_time = date_and_time + timedelta(hours=2)
        self.assertTrue(tag_stamp(DB, date_and_time.date(), date_and_time.time(),
                                  stamp, lorem.paragraph()))
        # Stamp out
        self.assertTrue(end_stamp(DB, date_and_time.date(), date_and_time.time()))

        # Create another workday a day later
        date_and_time = date_and_time + timedelta(days=1)
        # Stamp in
        stamp = new_stamp(DB, CUSTOMER_NAME, PROJECT_NAME, date_and_time.date(),
                         date_and_time.time(), ask=False)
        self.assertTrue(stamp)
        # Tag with current time
        self.assertTrue(tag_stamp(DB, date_and_time.date(), date_and_time.time(),
                                  stamp, lorem.paragraph()))
        # Tag with 1 added hour
        date_and_time = date_and_time + timedelta(hours=1)
        self.assertTrue(tag_stamp(DB, date_and_time.date(), date_and_time.time(),
                                  stamp, lorem.paragraph()))
        # Tag with 3 added hours
        date_and_time = date_and_time + timedelta(hours=2)
        self.assertTrue(tag_stamp(DB, date_and_time.date(), date_and_time.time(),
                                  stamp, lorem.paragraph()))
        # Stamp out
        self.assertTrue(end_stamp(DB, date_and_time.date(), date_and_time.time()))

        # Create another workday a day before
        date_and_time = date_and_time + timedelta(days=-2)
        # Stamp in
        stamp = new_stamp(DB, CUSTOMER_NAME, PROJECT_NAME, date_and_time.date(),
                         date_and_time.time(), ask=False)
        self.assertTrue(stamp)
        # Tag with current time
        self.assertTrue(tag_stamp(DB, date_and_time.date(), date_and_time.time(),
                                  stamp, lorem.paragraph()))
        # Tag with 1 added hour
        date_and_time = date_and_time + timedelta(hours=1)
        self.assertTrue(tag_stamp(DB, date_and_time.date(), date_and_time.time(),
                                  stamp, lorem.paragraph()))
        # Tag with 3 added hours
        date_and_time = date_and_time + timedelta(hours=2)
        self.assertTrue(tag_stamp(DB, date_and_time.date(), date_and_time.time(),
                                  stamp, lorem.paragraph()))
        # Tag with 5 added hours
        date_and_time = date_and_time + timedelta(hours=2)
        self.assertTrue(tag_stamp(DB, date_and_time.date(), date_and_time.time(),
                                  stamp, lorem.paragraph()))
        # Stamp out
        self.assertTrue(end_stamp(DB, date_and_time.date(), date_and_time.time()))

        # Create another workday to test workday deletion
        # Stamp in
        stamp = new_stamp(DB, CUSTOMER_NAME, PROJECT_NAME, date_and_time.date(),
                         date_and_time.time(), ask=False)
        self.assertTrue(stamp)
        # Tag with current time
        self.assertTrue(tag_stamp(DB, date_and_time.date(), date_and_time.time(),
                                  stamp, 'This should be deleted.'))
        # Tag with 1 added hour
        date_and_time = date_and_time + timedelta(hours=1)
        self.assertTrue(tag_stamp(DB, date_and_time.date(), date_and_time.time(),
                                  stamp, 'This should be deleted.'))
        # Tag with 3 added hours
        date_and_time = date_and_time + timedelta(hours=2)
        self.assertTrue(tag_stamp(DB, date_and_time.date(), date_and_time.time(),
                                  stamp, 'This should be deleted.'))
        # Tag with 5 added hours
        date_and_time = date_and_time + timedelta(hours=2)
        self.assertTrue(tag_stamp(DB, date_and_time.date(), date_and_time.time(),
                                  stamp, 'This should be deleted.'))
        # Stamp out
        self.assertTrue(end_stamp(DB, date_and_time.date(), date_and_time.time()))
        # Delete
        delete_workday_or_tag(DB, stamp.id)

        # Create another workday to test tag deletion
        date_and_time = datetime.now() + timedelta(days=10)
        # Stamp in
        stamp = new_stamp(DB, CUSTOMER_NAME, PROJECT_NAME, date_and_time.date(),
                          date_and_time.time(), ask=False)
        self.assertTrue(stamp)
        # Tag with current time
        tag = tag_stamp(DB, date_and_time.date(), date_and_time.time(),
                        stamp, 'This should be deleted.')
        self.assertTrue(tag)
        # Tag with 1 added hour
        date_and_time = date_and_time + timedelta(hours=1)
        self.assertTrue(tag_stamp(DB, date_and_time.date(), date_and_time.time(),
                                  stamp, 'This should not be deleted.'))
        # Tag with 3 added hours
        date_and_time = date_and_time + timedelta(hours=2)
        self.assertTrue(tag_stamp(DB, date_and_time.date(), date_and_time.time(),
                                  stamp, 'This should not be deleted.'))
        # Tag with 5 added hours
        date_and_time = date_and_time + timedelta(hours=2)
        self.assertTrue(tag_stamp(DB, date_and_time.date(), date_and_time.time(),
                                  stamp, 'This should not be deleted.'))
        # Stamp out
        self.assertTrue(end_stamp(DB, date_and_time.date(), date_and_time.time()))
        # Delete
        delete_workday_or_tag(DB, stamp.id, tag.id)

        # Status of workdays
        status_object = Status(DB.get('Workday', None), CONFIG)
        print(status_object)

        pdf = export_invoice(DB, '{:%Y}'.format(datetime.now()),
                             '{:%B}'.format(datetime.now()), CUSTOMER_NAME,
                             PROJECT_NAME, CONFIG, save_pdf=True, ask=False)
        print(pdf)
        os.system('xdg-open ' + '\'%s\'' % pdf)



def tearDownModule():
    if os.path.isfile(TESTING_DB_PATH):
        os.remove(TESTING_DB_PATH)
    invoice_folder = os.path.join(INVOICE_DIR, TESTING_DB)
    if os.path.isdir(invoice_folder):
        rmtree(invoice_folder)


if __name__ == '__main__':
    unittest.main()
