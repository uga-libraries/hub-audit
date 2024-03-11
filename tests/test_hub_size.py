"""
Test for the function hub_size(), which calculates the total size of all Hub shares
using a list of Hub share paths that are part of the function.
"""
import unittest
from hub_audit import hub_size


class MyTestCase(unittest.TestCase):

    def test_function(self):
        """Test for running the function. There is no input variation or error handling."""
        size = hub_size()
        size_expected = 0.15
        self.assertEqual(size, size_expected)


if __name__ == '__main__':
    unittest.main()
