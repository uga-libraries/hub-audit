"""
Tests for the function check_argument(), which verifies the required argument is present and a valid path.
In production, the input is from sys.argv
"""
import unittest
from hub_audit import check_argument
from os.path import join


class MyTestCase(unittest.TestCase):

    def test_correct(self):
        """Test for when the inventory argument is present and a valid path"""
        result = check_argument(['hub_audit.py', join('inventories', 'Digital Production Hub Inventory.xlsx')])
        expected = ('inventories\\Digital Production Hub Inventory.xlsx', None)
        self.assertEqual(result, expected, 'Problem with test for correct inventory argument')

    def test_inventory_missing(self):
        """Test for when the inventory argument is not present"""
        result = check_argument(['hub_audit.py'])
        expected = (None, 'Missing required argument: inventory')
        self.assertEqual(result, expected, 'Problem with test for inventory argument missing')

    def test_inventory_invalid(self):
        """Test for when the inventory argument is not a valid path"""
        result = check_argument(['hub_audit.py', 'error/Digital Production Hub Inventory.xlsx'])
        expected = (None, 'Provided inventory "error/Digital Production Hub Inventory.xlsx" does not exist')
        self.assertEqual(result, expected, 'Problem with test for correct inventory argument')

    def test_extra_argument(self):
        """Test for when there are too many arguments provided"""
        result = check_argument(['hub_audit.py', join('inventories', 'Digital Production Hub Inventory.xlsx'), 'extra'])
        expected = (None, 'Too many arguments. Should just have one argument, inventory')
        self.assertEqual(result, expected, 'Problem with test for extra argument')


if __name__ == '__main__':
    unittest.main()
