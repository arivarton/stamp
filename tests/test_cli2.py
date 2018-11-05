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

testing_db = 'test_%s' % uuid4().hex
testing_db_path = os.path.join(settings.DATA_DIR, testing_db) + '.db'
with patch('sys.stdin.read', return_value='y'), patch('builtins.input', lambda: 'test value'):
    db = Database(testing_db_path)
customer_name = 'Test Company AS'
project_name = 'Test Project'
current_date = datetime.now().date()
current_time = datetime.now().time().replace(second=0, microsecond=0)


# [TODO] Need to patch properly for stdin
class TestStampCLI(unittest.TestCase):

    def test_completing_workday_with_tags(self):
        with patch('sys.stdin.read', return_value='y'), patch('builtins.input', lambda: 'test value'):
            # Stamp in
            stamp = stamp_in(db, customer_name, project_name, current_date,
                             current_time)
            self.assertTrue(stamp)

            # Tag
            self.assertTrue(tag_stamp(db, current_date, current_time, stamp,
                                      lorem.paragraph()))


def tearDownModule():
    if os.path.isfile(testing_db_path):
        os.remove(testing_db_path)
    invoice_folder = os.path.join(settings.INVOICE_DIR, testing_db)
    if os.path.isdir(invoice_folder):
        rmtree(invoice_folder)


if __name__ == '__main__':
    unittest.main()
