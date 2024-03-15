"""
Tests for the function check_inventory(), which compares the inventory to the shares.

For easier testing, the variables with the contents of config.py (usually imported by the script)
and inventory_df (usually made by reading an Excel spreadsheet with read_inventory())
are made within the test functions.
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

    def setUp(self):
        """Variable used in all the tests."""
        self.columns = ['Share (required)', 'Folder Name (required if not share)', 'Use Policy Category (required)',
                        'Person Responsible (required)', 'Date to review for deletion (required)',
                        'Additional information (optional)', 'Deleted (date) (optional)', 'Audit_Result']

    def test_correct_second(self):
        """Test for a share where some second level folders are included and the share matches the inventory"""
        # Makes variables for function input and run the function being tested.
        config_shares = [{'name': 'Second_Level', 'path': join('shares', 'Second_Level'), 'pattern': 'second',
                          'folders': ['S_1', 'S_3']}]
        rows = [['Second_Level', 'S_1\\S_1a', 'Access/Mezzanine', 'JD', 'permanent', NaN, NaN, NaN],
                ['Second_Level', 'S_1\\S_1b', 'Access/Mezzanine', 'JD', 'permanent', NaN, NaN, NaN],
                ['Second_Level', 'S_2', 'Access/Mezzanine', 'JD', 'permanent', NaN, NaN, NaN],
                ['Second_Level', 'S_3\\S_3a', 'Access/Mezzanine', 'JD', 'permanent', NaN, NaN, NaN],
                ['Second_Level', 'S_3\\S_3b', 'Access/Mezzanine', 'JD', 'permanent', NaN, NaN, NaN]]
        inventory_df = check_inventory(DataFrame(rows, columns=self.columns), config_shares)

        # Tests if the resulting dataframe has the expected data.
        result = df_to_list(inventory_df)
        # expected = [self.columns,
        #             ['Second_Level', 'S_1\\S_1a', 'Access/Mezzanine', 'JD', 'permanent', 'nan', 'nan', 'nan'],
        #             ['Second_Level', 'S_1\\S_1b', 'Access/Mezzanine', 'JD', 'permanent', 'nan', 'nan', 'nan'],
        #             ['Second_Level', 'S_2', 'Access/Mezzanine', 'JD', 'permanent', 'nan', 'nan', 'nan'],
        #             ['Second_Level', 'S_3\\S_3a', 'Access/Mezzanine', 'JD', 'permanent', 'nan', 'nan', 'nan'],
        #             ['Second_Level', 'S_3\\S_3b', 'Access/Mezzanine', 'JD', 'permanent', 'nan', 'nan', 'nan']]
        expected = [['Share_Name', 'Share_Folder'], ['Second_Level', 'S_1\\S_1a'], ['Second_Level', 'S_1\\S_1b'],
                    ['Second_Level', 'S_2'], ['Second_Level', 'S_3\\S_3a'], ['Second_Level', 'S_3\\S_3b']]
        self.assertEqual(result, expected, "Problem with test for correct, second level folders")

    def test_correct_share(self):
        """Test for a share where the inventory is just the share name and the share matches the inventory"""
        # Makes variables for function input and run the function being tested.
        config_shares = [{'name': 'mezz_one', 'path': join('shares', 'mezz_one'), 'pattern': 'share', 'folders': []}]
        rows = [['mezz_one', 'mezz_one', 'Access/Mezzanine', 'JD', 'permanent', NaN, NaN, NaN]]
        inventory_df = check_inventory(DataFrame(rows, columns=self.columns), config_shares)

        # Tests if the resulting dataframe has the expected data.
        result = df_to_list(inventory_df)
        # expected = [self.columns,
        #             ['mezz_one', 'mezz_one', 'Access/Mezzanine', 'JD', 'permanent', 'nan', 'nan', 'nan']]
        expected = [['Share_Name', 'Share_Folder'],
                    ['mezz_one', 'mezz_one']]
        self.assertEqual(result, expected, "Problem with test for correct, share name")

    def test_correct_top(self):
        """Test for a share where only top level folders are included and the share matches the inventory"""
        # Makes variables for function input and run the function being tested.
        config_shares = [{'name': 'Top', 'path': join('shares', 'Top'), 'pattern': 'top', 'folders': []}]
        rows = [['Top', 'T_1', 'Access/Mezzanine', 'JD', 'permanent', NaN, NaN, NaN],
                ['Top', 'T_2', 'Access/Mezzanine', 'JD', 'permanent', NaN, NaN, NaN]]
        inventory_df = check_inventory(DataFrame(rows, columns=self.columns), config_shares)

        # Tests if the resulting dataframe has the expected data.
        result = df_to_list(inventory_df)
        # expected = [self.columns,
        #             ['Top', 'T_1', 'Access/Mezzanine', 'JD', 'permanent', 'nan', 'nan', 'nan'],
        #             ['Top', 'T_2', 'Access/Mezzanine', 'JD', 'permanent', 'nan', 'nan', 'nan']]
        expected = [['Share_Name', "Share_Folder"], ['Top', 'T_1'], ['Top', 'T_2']]
        self.assertEqual(result, expected, "Problem with test for correct, top folders")

    def test_error_extra_file(self):
        """Test for when a share has a file at the top level of the share, instead of just folders"""
        # Makes variables for function input and run the function being tested.
        config_shares = [{'name': 'Extra', 'path': join('shares', 'Extra'), 'pattern': 'top', 'folders': []}]
        rows = [['Extra', 'E_1', 'Access/Mezzanine', 'JD', 'permanent', NaN, NaN, NaN],
                ['Extra', 'E_2', 'Access/Mezzanine', 'JD', 'permanent', NaN, NaN, NaN]]
        inventory_df = check_inventory(DataFrame(rows, columns=self.columns), config_shares)

        # Tests if the resulting dataframe has the expected data.
        result = df_to_list(inventory_df)
        # expected = [self.columns,
        #             ['Extra', 'E_1', 'Access/Mezzanine', 'JD', 'permanent', 'nan', 'nan', 'nan'],
        #             ['Extra', 'E_2', 'Access/Mezzanine', 'JD', 'permanent', 'nan', 'nan', 'nan']]
        expected = [['Share_Name', 'Share_Folder'], ['Extra', 'E_1'], ['Extra', 'E_2'], ['Extra', 'Text.txt']]
        self.assertEqual(result, expected, "Problem with test for error, extra file")


if __name__ == '__main__':
    unittest.main()
