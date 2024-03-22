"""
Tests for the function check_arguments(), which verifies the required arguments are present and valid paths.
In production, the input is from sys.argv
"""
import unittest
from hub_audit import check_arguments
from os.path import join


class MyTestCase(unittest.TestCase):

    def test_both_correct(self):
        """Test for when both arguments are present and valid paths"""
        args = ['hub_audit.py', join('inventories', 'Digital Production Hub Inventory.xlsx'), 'test_shares.csv']
        result = check_arguments(args)
        expected = ('inventories\\Digital Production Hub Inventory.xlsx', 'test_shares.csv', [])
        self.assertEqual(result, expected, 'Problem with test for both arguments correct')

    def test_both_invalid(self):
        """Test for when both arguments are present but not valid paths"""
        args = ['hub_audit.py', join('error', 'Digital Production Hub Inventory.xlsx'), 'error_shares.csv']
        result = check_arguments(args)
        expected = (None, None, ['Provided inventory "error\\Digital Production Hub Inventory.xlsx" does not exist',
                                 'Provided share information "error_shares.csv" does not exist'])
        self.assertEqual(result, expected, 'Problem with test for both arguments invalid')

    def test_both_missing(self):
        """Test for when both arguments are not present"""
        args = ['hub_audit.py']
        result = check_arguments(args)
        expected = (None, None, ['Missing both required arguments, inventory and share information'])
        self.assertEqual(result, expected, 'Problem with test for both arguments missing')

    def test_inventory_invalid(self):
        """Test for when the inventory argument is not a valid path"""
        args = ['hub_audit.py', join('error', 'Digital Production Hub Inventory.xlsx'), 'test_shares.csv']
        result = check_arguments(args)
        expected = (None, 'test_shares.csv',
                    ['Provided inventory "error\\Digital Production Hub Inventory.xlsx" does not exist'])
        self.assertEqual(result, expected, 'Problem with test for inventory argument invalid')

    def test_inventory_missing(self):
        """Test for when the share information argument is not present"""
        args = ['hub_audit.py', 'test_shares.csv']
        result = check_arguments(args)
        expected = (None, None, ['Missing one of the required arguments, inventory or share information'])
        self.assertEqual(result, expected, 'Problem with test for inventory argument missing')

    def test_share_invalid(self):
        """Test for when the share information argument is not a valid path"""
        args = ['hub_audit.py', join('inventories', 'Digital Production Hub Inventory.xlsx'), 'error_shares.csv']
        result = check_arguments(args)
        expected = ('inventories\\Digital Production Hub Inventory.xlsx', None,
                    ['Provided share information "error_shares.csv" does not exist'])
        self.assertEqual(result, expected, 'Problem with test for share argument invalid')

    def test_share_missing(self):
        """Test for when the share information argument is not present"""
        args = ['hub_audit.py', join('inventories', 'Digital Production Hub Inventory.xlsx')]
        result = check_arguments(args)
        expected = (None, None, ['Missing one of the required arguments, inventory or share information'])
        self.assertEqual(result, expected, 'Problem with test for share argument missing')

    def test_extra_argument(self):
        """Test for when there are too many arguments provided"""
        args = ['hub_audit.py', join('inventories', 'Digital Production Hub Inventory.xlsx'), 'test_shares.csv', 'x']
        result = check_arguments(args)
        expected = (None, None, ['Too many arguments. Should have two arguments, inventory and share information'])
        self.assertEqual(result, expected, 'Problem with test for extra argument')


if __name__ == '__main__':
    unittest.main()
