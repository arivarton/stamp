import os
import sys
import unittest
from unittest.mock import patch

sys.path.append('../stamp')

from stamp import stamp # NOQA

testing_db = 'test'


class TestStringMethods(unittest.TestCase):
    @patch('builtins.input', lambda: 'y')
    def test_add(self):
        parser = stamp.parse_args(['add', '-c', 'test_company', '-p', 'test_project', '--db', testing_db])
        os.remove(parser.db)
        self.assertTrue(parser.func(parser))

    def test_end(self):
        parser = stamp.parse_args(['end', '--db', testing_db])
        self.assertTrue(parser.func(parser))

    def test_status(self):
        parser = stamp.parse_args(['status', '--db', testing_db])
        self.assertTrue(parser.func(parser))


if __name__ == '__main__':
    unittest.main()
