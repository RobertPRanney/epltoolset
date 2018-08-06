"""
FILE: test_credentials.py
AUTHOR: Robert Ranney
DESCR: Test the credentials class
USAGE: Run with unittest test discovery
"""

import unittest

from epltoolset.pdConnection import Credentials

class TestCredentials(unittest.TestCase):
    """Test Credentials Class"""
    def setUp(self):
        """Run Before Tests"""
        pass


    def tearDown(self):
        """Run After Tests"""
        pass


    def test_can_initialize(self):
        """Test that a credentials object can be instantiated"""
        obj = Credentials()
        self.assertIsNotNone(obj)
        self.assertIsInstance(obj, Credentials)


    def test_attribute_types(self):
        """Make sure all attrs present and of correct type on instantion"""
        obj = Credentials('test', 15, 'test', 'test', 'test')
        self.assertIsInstance(obj.host, str)
        self.assertIsInstance(obj.port, int)
        self.assertIsInstance(obj.username, str)
        self.assertIsInstance(obj.sid, str),
        self.assertIsInstance(obj.password, str)


    def test_is_complete(self):
        """make sure credentials can return a nice dictionary"""
        obj = Credentials('test', 15, 'test', 'test', 'test')
        attrs = obj.attrs()
        self.assertIsNotNone(attrs)
        self.assertIsInstance(attrs, dict)
        self.assertTrue('host' in attrs)
        self.assertTrue('port' in attrs)
        self.assertTrue('sid' in attrs)
        self.assertTrue('username' in attrs)
        self.assertTrue('password' in attrs)


    def test_print_string(self):
        """make sure string represtiation function works"""
        obj = Credentials('test', 15, 'test', 'test', 'test')
        self.assertIsInstance(obj.__str__(), str)
