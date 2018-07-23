import unittest

import epltoolset

class TestSomething(unittest.TestCase):
    def test_is_string(self):
        s = epltoolset.something.hello()
        self.assertTrue(isinstance(s, str))
