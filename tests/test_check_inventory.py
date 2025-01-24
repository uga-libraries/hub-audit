"""
Tests for the function check_inventory(), which compares the inventory to the shares.

To simply testing, the inventory df only includes columns needed for the comparison.
"""
import unittest
from hub_audit import check_inventory
from numpy import NaN
from os.path import join
from pandas import DataFrame


def df_to_list(df):
    """Fill blanks with the string 'nan' and convert each row in a dataframe to a list"""
    df = df.fillna('nan')
    df_list = [df.columns.tolist()] + df.values.tolist()
    return df_list


class MyTestCase(unittest.TestCase):

    def test_match(self):
        """Test for when the inventory matches the share contents"""
        # Makes variables for function input and run the function being tested.
        inventory_df = DataFrame([['share_a', 'folder_a', NaN],
                                  ['share_a', 'file.txt', NaN],
                                  ['share_b', 'folder_b\\folder_b1', NaN],
                                  ['share_c', 'born-digital\\closed\\folder', NaN]],
                                 columns=['Share', 'Folder', 'Audit_Inventory'])
        shares_df = DataFrame([['share_a', 'folder_a'],
                               ['share_a', 'file.txt'],
                               ['share_b', 'folder_b\\folder_b1'],
                               ['share_c', 'born-digital\\closed\\folder']],
                              columns=['Share', 'Folder'])
        inventory_df = check_inventory(inventory_df, shares_df)

        # Tests if the resulting dataframe has the expected data.
        result = df_to_list(inventory_df)
        expected = [['Share', 'Folder', 'Audit_Inventory'],
                    ['share_a', 'file.txt', 'Correct'],
                    ['share_a', 'folder_a', 'Correct'],
                    ['share_b', 'folder_b\\folder_b1', 'Correct'],
                    ['share_c', 'born-digital\\closed\\folder', 'Correct']]
        self.assertEqual(result, expected, "Problem with test for match")

    def test_match_duplicates(self):
        """Test for when the inventory matches the share contents, which has duplicate rows"""
        # Makes variables for function input and run the function being tested.
        inventory_df = DataFrame([['share_a', 'folder_a', NaN],
                                  ['share_a', 'file.txt', NaN],
                                  ['share_b', 'folder_b\\folder_b1', NaN],
                                  ['share_c', 'born-digital\\closed\\folder', NaN]],
                                 columns=['Share', 'Folder', 'Audit_Inventory'])
        shares_df = DataFrame([['share_a', 'folder_a'],
                               ['share_a', 'folder_a'],
                               ['share_a', 'folder_a'],
                               ['share_a', 'file.txt'],
                               ['share_b', 'folder_b\\folder_b1'],
                               ['share_b', 'folder_b\\folder_b1'],
                               ['share_c', 'born-digital\\closed\\folder']],
                              columns=['Share', 'Folder'])
        inventory_df = check_inventory(inventory_df, shares_df)

        # Tests if the resulting dataframe has the expected data.
        result = df_to_list(inventory_df)
        expected = [['Share', 'Folder', 'Audit_Inventory'],
                    ['share_a', 'file.txt', 'Correct'],
                    ['share_a', 'folder_a', 'Correct'],
                    ['share_b', 'folder_b\\folder_b1', 'Correct'],
                    ['share_c', 'born-digital\\closed\\folder', 'Correct']]
        self.assertEqual(result, expected, "Problem with test for match, duplicates")

    def test_not_inventory(self):
        """Test for when some rows are only in the share and not the inventory"""
        # Makes variables for function input and run the function being tested.
        inventory_df = DataFrame([['share_a', 'folder_a', NaN],
                                  ['share_a', 'file.txt', NaN]],
                                 columns=['Share', 'Folder', 'Audit_Inventory'])
        shares_df = DataFrame([['share_a', 'file.txt'],
                               ['share_a', 'folder_a'],
                               ['share_b', 'file.txt'],
                               ['share_b', 'folder_b\\folder_b1'],
                               ['share_c', 'born-digital\\closed\\folder']],
                              columns=['Share', 'Folder'])
        inventory_df = check_inventory(inventory_df, shares_df)

        # Tests if the resulting dataframe has the expected data.
        result = df_to_list(inventory_df)
        expected = [['Share', 'Folder', 'Audit_Inventory'],
                    ['share_a', 'file.txt', 'Correct'],
                    ['share_a', 'folder_a', 'Correct'],
                    ['share_b', 'file.txt', 'Not in inventory'],
                    ['share_b', 'folder_b\\folder_b1', 'Not in inventory'],
                    ['share_c', 'born-digital\\closed\\folder', 'Not in inventory']]
        self.assertEqual(result, expected, "Problem with test for not in inventory")

    def test_not_share(self):
        """Test for when some rows are only in the inventory and not the share"""
        # Makes variables for function input and run the function being tested.
        inventory_df = DataFrame([['share_a', 'born-digital\\closed\\folder', NaN],
                                  ['share_a', 'folder_a', NaN],
                                  ['share_a', 'file.txt', NaN],
                                  ['share_b', 'folder_b\\folder_b1', NaN],
                                  ['share_c', 'born-digital\\closed\\folder', NaN]],
                                 columns=['Share', 'Folder', 'Audit_Inventory'])
        shares_df = DataFrame([['share_a', 'folder_a'],
                               ['share_c', 'born-digital\\closed\\folder']],
                              columns=['Share', 'Folder'])
        inventory_df = check_inventory(inventory_df, shares_df)

        # Tests if the resulting dataframe has the expected data.
        result = df_to_list(inventory_df)
        expected = [['Share', 'Folder', 'Audit_Inventory'],
                    ['share_a', 'born-digital\\closed\\folder', 'Not in share'],
                    ['share_a', 'file.txt', 'Not in share'],
                    ['share_a', 'folder_a', 'Correct'],
                    ['share_b', 'folder_b\\folder_b1', 'Not in share'],
                    ['share_c', 'born-digital\\closed\\folder', 'Correct']]
        self.assertEqual(result, expected, "Problem with test for not in share")

    def test_variety(self):
        """Test for when some rows are just in the inventory, some just in the share, and some match"""
        # Makes variables for function input and run the function being tested.
        inventory_df = DataFrame([['share_c', 'born-digital\\closed\\folder', NaN],
                                  ['share_a', 'folder_a', NaN],
                                  ['share_a', 'file.txt', NaN]],
                                 columns=['Share', 'Folder', 'Audit_Inventory'])
        shares_df = DataFrame([['share_a', 'folder_a'],
                               ['share_b', 'file.txt'],
                               ['share_b', 'folder_b\\folder_b1'],
                               ['share_c', 'born-digital\\closed\\folder']],
                              columns=['Share', 'Folder'])
        inventory_df = check_inventory(inventory_df, shares_df)

        # Tests if the resulting dataframe has the expected data.
        result = df_to_list(inventory_df)
        expected = [['Share', 'Folder', 'Audit_Inventory'],
                    ['share_a', 'file.txt', 'Not in share'],
                    ['share_a', 'folder_a', 'Correct'],
                    ['share_b', 'file.txt', 'Not in inventory'],
                    ['share_b', 'folder_b\\folder_b1', 'Not in inventory'],
                    ['share_c', 'born-digital\\closed\\folder', 'Correct']]
        self.assertEqual(result, expected, "Problem with test for variety")


if __name__ == '__main__':
    unittest.main()
