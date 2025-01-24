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
        """Test for the pattern share"""
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


if __name__ == '__main__':
    unittest.main()
