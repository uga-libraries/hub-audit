"""
Tests for the function check_required(), which finds missing values in required columns.

For easier testing, the dataframe with inventory data is made within the function using pandas.
In production, it is made by reading an Excel spreadsheet using read_inventory().
"""
import unittest
from hub_audit import check_required
from numpy import NaN
from pandas import DataFrame


def df_to_list(df):
    """Fill blanks with the string 'nan' and convert each row in a dataframe to a list"""
    df = df.fillna('nan')
    df_list = [df.columns.tolist()] + df.values.tolist()
    return df_list


class MyTestCase(unittest.TestCase):

    def setUp(self):
        """Variable used in all the tests."""
        self.columns = ['Share', 'Folder', 'Use', 'Responsible', 'Review_Date', 'Notes', 'Deleted_Date', 
                        'Audit_Dates', 'Audit_Inventory', 'Audit_Required']

    def test_complete(self):
        """Test for an inventory with data in all required columns"""
        # Make a dataframe with Hub inventory data and run the function being tested.
        rows = [['Share', 'Folder1', 'Medium Priority', 'Bill', 'Permanent', NaN, NaN, NaN, NaN, NaN],
                ['Share', 'Folder2', 'Medium Priority', 'Bill', 'Permanent', NaN, NaN, NaN, NaN, NaN],
                ['Share', 'Folder3', 'Medium Priority', 'Bill', 'Permanent', NaN, NaN, NaN, NaN, NaN]]
        inventory_df = check_required(DataFrame(rows, columns=self.columns))

        # Tests if the resulting dataframe has the expected data.
        result = df_to_list(inventory_df)
        expected = [self.columns,
                    ['Share', 'Folder1', 'Medium Priority', 'Bill', 'Permanent', 'nan', 'nan', 'nan', 'nan', 'Correct'],
                    ['Share', 'Folder2', 'Medium Priority', 'Bill', 'Permanent', 'nan', 'nan', 'nan', 'nan', 'Correct'],
                    ['Share', 'Folder3', 'Medium Priority', 'Bill', 'Permanent', 'nan', 'nan', 'nan', 'nan', 'Correct']]
        self.assertEqual(result, expected, "Problem with test for complete data")

    def test_missing_combination(self):
        """Test for an inventory missing data in multiple required columns"""
        # Make a dataframe with Hub inventory data and run the function being tested.
        rows = [[NaN, NaN, 'Medium Priority', NaN, 'Permanent', NaN, NaN, NaN, NaN, NaN],
                [NaN, NaN, NaN, NaN, NaN, NaN, NaN, 'Note', NaN, NaN],
                ['Share', 'Folder3', NaN, 'Bill', NaN, NaN, NaN, NaN, NaN, NaN]]
        inventory_df = check_required(DataFrame(rows, columns=self.columns))

        # Tests if the resulting dataframe has the expected data.
        result = df_to_list(inventory_df)
        expected = [self.columns,
                    ['nan', 'nan', 'Medium Priority', 'nan', 'Permanent', 'nan', 'nan', 'nan', 'nan', 'Missing'],
                    ['nan', 'nan', 'nan', 'nan', 'nan', 'nan', 'nan', 'Note', 'nan', 'Missing'],
                    ['Share', 'Folder3', 'nan', 'Bill', 'nan', 'nan', 'nan', 'nan', 'nan', 'Missing']]
        self.assertEqual(result, expected, "Problem with test for missing combinations of required columns")

    def test_missing_date(self):
        """Test for an inventory missing data in the "Date to review for deletion" column"""
        # Make a dataframe with Hub inventory data and run the function being tested.
        rows = [['Share', 'Folder1', 'Medium Priority', 'Bill', NaN, NaN, NaN, NaN, NaN, NaN],
                ['Share', 'Folder2', 'Medium Priority', 'Bill', NaN, NaN, NaN, NaN, NaN, NaN],
                ['Share', 'Folder3', 'Medium Priority', 'Bill', 'Permanent', NaN, NaN, NaN, NaN, NaN]]
        inventory_df = check_required(DataFrame(rows, columns=self.columns))

        # Tests if the resulting dataframe has the expected data.
        result = df_to_list(inventory_df)
        expected = [self.columns,
                    ['Share', 'Folder1', 'Medium Priority', 'Bill', 'nan', 'nan', 'nan', 'nan', 'nan', 'Missing'],
                    ['Share', 'Folder2', 'Medium Priority', 'Bill', 'nan', 'nan', 'nan', 'nan', 'nan', 'Missing'],
                    ['Share', 'Folder3', 'Medium Priority', 'Bill', 'Permanent', 'nan', 'nan', 'nan', 'nan', 'Correct']]
        self.assertEqual(result, expected, "Problem with test for missing date to review for deletion")

    def test_missing_folder(self):
        """Test for an inventory missing data in the "Folder Name" column"""
        # Make a dataframe with Hub inventory data and run the function being tested.
        rows = [['Share', 'Folder1', 'Medium Priority', 'Bill', 'Permanent', NaN, NaN, NaN, NaN, NaN],
                ['Share', NaN, 'Medium Priority', 'Bill', 'Permanent', NaN, NaN, NaN, NaN, NaN],
                ['Share', NaN, 'Medium Priority', 'Bill', 'Permanent', NaN, NaN, NaN, NaN, NaN]]
        inventory_df = check_required(DataFrame(rows, columns=self.columns))

        # Tests if the resulting dataframe has the expected data.
        result = df_to_list(inventory_df)
        expected = [self.columns,
                    ['Share', 'Folder1', 'Medium Priority', 'Bill', 'Permanent', 'nan', 'nan', 'nan', 'nan', 'Correct'],
                    ['Share', 'nan', 'Medium Priority', 'Bill', 'Permanent', 'nan', 'nan', 'nan', 'nan', 'Missing'],
                    ['Share', 'nan', 'Medium Priority', 'Bill', 'Permanent', 'nan', 'nan', 'nan', 'nan', 'Missing']]
        self.assertEqual(result, expected, "Problem with test for missing folder name")

    def test_missing_person(self):
        """Test for an inventory missing data in the "Person Responsible" column"""
        # Make a dataframe with Hub inventory data and run the function being tested.
        rows = [['Share', 'Folder1', 'Medium Priority', NaN, 'Permanent', NaN, NaN, NaN, NaN, NaN],
                ['Share', 'Folder2', 'Medium Priority', NaN, 'Permanent', NaN, NaN, NaN, NaN, NaN],
                ['Share', 'Folder3', 'Medium Priority', NaN, 'Permanent', NaN, NaN, NaN, NaN, NaN]]
        inventory_df = check_required(DataFrame(rows, columns=self.columns))

        # Tests if the resulting dataframe has the expected data.
        result = df_to_list(inventory_df)
        expected = [self.columns,
                    ['Share', 'Folder1', 'Medium Priority', 'nan', 'Permanent', 'nan', 'nan', 'nan', 'nan', 'Missing'],
                    ['Share', 'Folder2', 'Medium Priority', 'nan', 'Permanent', 'nan', 'nan', 'nan', 'nan', 'Missing'],
                    ['Share', 'Folder3', 'Medium Priority', 'nan', 'Permanent', 'nan', 'nan', 'nan', 'nan', 'Missing']]
        self.assertEqual(result, expected, "Problem with test for missing person responsible")

    def test_missing_share(self):
        """Test for an inventory missing data in the "Share" column"""
        # Make a dataframe with Hub inventory data and run the function being tested.
        rows = [[NaN, 'Folder1', 'Medium Priority', 'Bill', 'Permanent', NaN, NaN, NaN, NaN, NaN],
                ['Share', 'Folder2', 'Medium Priority', 'Bill', 'Permanent', NaN, NaN, NaN, NaN, NaN],
                [NaN, 'Folder3', 'Medium Priority', 'Bill', 'Permanent', NaN, NaN, NaN, NaN, NaN]]
        inventory_df = check_required(DataFrame(rows, columns=self.columns))

        # Tests if the resulting dataframe has the expected data.
        result = df_to_list(inventory_df)
        expected = [self.columns,
                    ['nan', 'Folder1', 'Medium Priority', 'Bill', 'Permanent', 'nan', 'nan', 'nan', 'nan', 'Missing'],
                    ['Share', 'Folder2', 'Medium Priority', 'Bill', 'Permanent', 'nan', 'nan', 'nan', 'nan', 'Correct'],
                    ['nan', 'Folder3', 'Medium Priority', 'Bill', 'Permanent', 'nan', 'nan', 'nan', 'nan', 'Missing']]
        self.assertEqual(result, expected, "Problem with test for missing share")

    def test_missing_use(self):
        """Test for an inventory missing data in the "Use Policy Category" column"""
        # Make a dataframe with Hub inventory data and run the function being tested.
        rows = [['Share', 'Folder1', 'Medium Priority', 'Bill', 'Permanent', NaN, NaN, NaN, NaN, NaN],
                ['Share', 'Folder2', 'Medium Priority', 'Bill', 'Permanent', NaN, NaN, NaN, NaN, NaN],
                ['Share', 'Folder3', NaN, 'Bill', 'Permanent', NaN, NaN, NaN, NaN, NaN]]
        inventory_df = check_required(DataFrame(rows, columns=self.columns))

        # Tests if the resulting dataframe has the expected data.
        result = df_to_list(inventory_df)
        expected = [self.columns,
                    ['Share', 'Folder1', 'Medium Priority', 'Bill', 'Permanent', 'nan', 'nan', 'nan', 'nan', 'Correct'],
                    ['Share', 'Folder2', 'Medium Priority', 'Bill', 'Permanent', 'nan', 'nan', 'nan', 'nan', 'Correct'],
                    ['Share', 'Folder3', 'nan', 'Bill', 'Permanent', 'nan', 'nan', 'nan', 'nan', 'Missing']]
        self.assertEqual(result, expected, "Problem with test for missing use policy category")


if __name__ == '__main__':
    unittest.main()
