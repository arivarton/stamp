import os
import sys
import unittest
from unittest.mock import patch

sys.path.append('../stamp')

from stamp import stamp, settings # NOQA

testing_db = 'test'
testing_db_path = os.path.join(settings.DATA_DIR, testing_db) + '.db'


class TestStampCLI(unittest.TestCase):

    @patch('builtins.input', lambda: 'y')
    def test_completing_workday_with_tags(self):
        parser = stamp.parse_args(['in', '-c', 'test_company', '-p',
                                   'test_project', '--db', testing_db])
        self.assertTrue(parser.func(parser))

        parser = stamp.parse_args(['tag', 'testing tag', '--db', testing_db])
        parser = stamp.parse_args(['tag', 'testing tag 2', '--db', testing_db])
        self.assertTrue(parser.func(parser))

        parser = stamp.parse_args(['out', '--db', testing_db])
        self.assertTrue(parser.func(parser))

        parser = stamp.parse_args(['status', '--db', testing_db])
        self.assertTrue(parser.func(parser))


def tearDownModule():
    os.remove(testing_db_path)


if __name__ == '__main__':
    unittest.main()
