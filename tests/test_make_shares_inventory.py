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
        """Test for an unexpected pattern (error)"""
        # Makes variable for function input and run the function being tested.
        shares_info_df = DataFrame([['a', 'make_inv\\share\\a', 'pattern error', NaN]],
                                   columns=['name', 'path', 'pattern', 'folders'])
        shares_df = make_shares_inventory(shares_info_df)

        # Tests if the resulting dataframe has the expected data (empty).
        result = df_to_list(shares_df)
        expected = [['Share', 'Folder']]
        self.assertEqual(result, expected, "Problem with test for unexpected")


if __name__ == '__main__':
    unittest.main()
