"""
Tests for the function make_shares_inventory(),
which makes a dataframe with the contents of all shares, to the level of detail specified in df_info.
"""
import unittest
from hub_audit import make_shares_inventory
from test_check_inventory import df_to_list
from numpy import NaN
from pandas import DataFrame


class MyTestCase(unittest.TestCase):

    def test_second(self):
        """Test for the 'second' pattern"""
        # Makes variable for function input and run the function being tested.
        shares_info_df = DataFrame([['a', 'make_inv\\second\\a', 'second', ''],
                                    ['b', 'make_inv\\second\\b', 'second', ''],
                                    ['c', 'make_inv\\second\\c', 'second', 'born-digital'],
                                    ['d', 'make_inv\\second\\d', 'second', 'born-digital'],
                                    ['e', 'make_inv\\second\\e', 'second', 'folder_2|folder_e']],
                                   columns=['name', 'path', 'pattern', 'folders'])
        shares_df = make_shares_inventory(shares_info_df)

        # Tests if the resulting dataframe has the expected data.
        result = df_to_list(shares_df)
        expected = [['Share', 'Folder'],
                    ['a', 'folder_a'],
                    ['b', 'folder_b'],
                    ['c', 'born-digital\\backlogged\\folder_c1'],
                    ['c', 'born-digital\\backlogged\\folder_c2'],
                    ['d', 'born-digital\\closed\\folder_d1'],
                    ['e', 'folder_2\\folder_e1'],
                    ['e', 'folder_2\\folder_e2'],
                    ['e', 'folder_3'],
                    ['e', 'folder_e\\folder_e1'],
                    ['e', 'folder_e\\folder_e2']]
        self.assertEqual(result, expected, "Problem with test for second")

    def test_share(self):
        """Test for the 'share' pattern"""
        # Makes variable for function input and run the function being tested.
        shares_info_df = DataFrame([['a', 'make_inv\\share\\a', 'share', NaN],
                                    ['b', 'make_inv\\share\\b', 'share', NaN]],
                                   columns=['name', 'path', 'pattern', 'folders'])
        shares_df = make_shares_inventory(shares_info_df)

        # Tests if the resulting dataframe has the expected data.
        result = df_to_list(shares_df)
        expected = [['Share', 'Folder'],
                    ['a', 'a'],
                    ['b', 'b']]
        self.assertEqual(result, expected, "Problem with test for share")

    def test_top(self):
        """Test for the 'top' pattern"""
        # Makes variable for function input and run the function being tested.
        shares_info_df = DataFrame([['a', 'make_inv\\top\\a', 'top', NaN],
                                    ['b', 'make_inv\\top\\b', 'top', NaN],
                                    ['c', 'make_inv\\top\\c', 'top', NaN],
                                    ['d', 'make_inv\\top\\d', 'top', NaN]],
                                   columns=['name', 'path', 'pattern', 'folders'])
        shares_df = make_shares_inventory(shares_info_df)

        # Tests if the resulting dataframe has the expected data.
        result = df_to_list(shares_df)
        expected = [['Share', 'Folder'],
                    ['a', 'folder_a1'],
                    ['a', 'folder_a2'],
                    ['b', 'folder_b'],
                    ['c', 'folder_c'],
                    ['d', 'File.txt'],
                    ['d', 'folder_d']]
        self.assertEqual(result, expected, "Problem with test for top")

    def test_unexpected(self):
        """Test for an unexpected pattern (error)
        It should also print 'Error: config has an unexpected pattern pattern_error'"""
        # Makes variable for function input and run the function being tested.
        shares_info_df = DataFrame([['a', 'make_inv\\share\\a', 'pattern_error', NaN]],
                                   columns=['name', 'path', 'pattern', 'folders'])
        shares_df = make_shares_inventory(shares_info_df)

        # Tests if the resulting dataframe has the expected data (empty).
        result = df_to_list(shares_df)
        expected = [['Share', 'Folder']]
        self.assertEqual(result, expected, "Problem with test for unexpected")


if __name__ == '__main__':
    unittest.main()
