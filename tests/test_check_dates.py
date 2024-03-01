"""
Tests for the function check_dates, which finds dates to review for deletion that have expired
"""
import unittest
from hub_audit import check_dates
from datetime import datetime
from numpy import NaN
from pandas import DataFrame


class MyTestCase(unittest.TestCase):

    def test_combination(self):
        """Test for an inventory where the date formatting is mixed"""
        # Makes a dataframe for function input, which would usually be made by read_inventory(), and runs the function.
        column_names = ['Share (required)', 'Folder Name (required if not share)', 'Use Policy Category (required)',
                        'Person Responsible (required)', 'Date to review for deletion (required)',
                        'Additional information (optional)', 'Deleted (date) (optional)', 'Audit_Result']
        df = DataFrame([['Share_A', 'FolderA1', 'Backlog', 'June', 'Permanent', NaN, NaN, NaN],
                        ['Share_A', 'FolderA2', 'Backlog', 'June', datetime(2021, 1, 1, 0, 0), NaN, NaN, NaN],
                        ['Share_B', 'FolderB', 'Backlog', 'June', '6 months', NaN, NaN, NaN],
                        ['Share_C', 'FolderC1', 'Backlog', 'June', datetime(3031, 12, 14, 0, 0), NaN, NaN, NaN],
                        ['Share_C', 'FolderC2', 'Backlog', 'June', 'permanent', NaN, NaN, NaN]],
                       columns=column_names)
        inventory_df = check_dates(df)

        # Converts the function result (dataframe) into a list, with blanks replaced by empty strings,
        # and compares it to the expected result.
        result = inventory_df.fillna('')
        result = [result.columns.tolist()] + result.values.tolist()
        expected = [column_names,
                    ['Share_A', 'FolderA1', 'Backlog', 'June', 'Permanent', '', '', ''],
                    ['Share_A', 'FolderA2', 'Backlog', 'June', datetime(2021, 1, 1, 0, 0), '', '', 'Date expired'],
                    ['Share_B', 'FolderB', 'Backlog', 'June', '6 months', '', '', 'Check date'],
                    ['Share_C', 'FolderC1', 'Backlog', 'June', datetime(3031, 12, 14, 0, 0), '', '', ''],
                    ['Share_C', 'FolderC2', 'Backlog', 'June', 'permanent', '', '', '']]
        self.assertEqual(result, expected, "Problem with test for combined date formats")

    def test_dates_expired(self):
        """Test for an inventory where the dates are formatted as a date and the dates are in the past (expired)"""

        # Makes a dataframe for function input, which would usually be made by read_inventory(), and runs the function.
        column_names = ['Share (required)', 'Folder Name (required if not share)', 'Use Policy Category (required)',
                        'Person Responsible (required)', 'Date to review for deletion (required)',
                        'Additional information (optional)', 'Deleted (date) (optional)', 'Audit_Result']
        df = DataFrame([['Share_A', 'FolderA1', 'Backlog', 'June', datetime(2024, 2, 29, 0, 0), NaN, NaN, NaN],
                        ['Share_A', 'FolderA2', 'Backlog', 'June', datetime(2024, 2, 1, 0, 0), NaN, NaN, NaN],
                        ['Share_B', 'FolderB', 'Backlog', 'June', datetime(2022, 10, 15, 0, 0), NaN, NaN, NaN]],
                       columns=column_names)
        inventory_df = check_dates(df)

        # Converts the function result (dataframe) into a list, with blanks replaced by empty strings,
        # and compares it to the expected result.
        result = inventory_df.fillna('')
        result = [result.columns.tolist()] + result.values.tolist()
        expected = [column_names,
                    ['Share_A', 'FolderA1', 'Backlog', 'June', datetime(2024, 2, 29, 0, 0), '', '', 'Date expired'],
                    ['Share_A', 'FolderA2', 'Backlog', 'June', datetime(2024, 2, 1, 0, 0), '', '', 'Date expired'],
                    ['Share_B', 'FolderB', 'Backlog', 'June', datetime(2022, 10, 15, 0, 0), '', '', 'Date expired']]
        self.assertEqual(result, expected, "Problem with test for dates, expired")

    def test_dates_future(self):
        """Test for an inventory where the dates are formatted as a date and the dates are in the future"""

        # Makes a dataframe for function input, which would usually be made by read_inventory(), and runs the function.
        column_names = ['Share (required)', 'Folder Name (required if not share)', 'Use Policy Category (required)',
                        'Person Responsible (required)', 'Date to review for deletion (required)',
                        'Additional information (optional)', 'Deleted (date) (optional)', 'Audit_Result']
        df = DataFrame([['Share_A', 'FolderA1', 'Backlog', 'June', datetime(2122, 10, 15, 0, 0), NaN, NaN, NaN],
                        ['Share_A', 'FolderA2', 'Backlog', 'June', datetime(2222, 10, 15, 0, 0), NaN, NaN, NaN],
                        ['Share_B', 'FolderB', 'Backlog', 'June', datetime(2322, 10, 15, 0, 0), NaN, NaN, NaN]],
                       columns=column_names)
        inventory_df = check_dates(df)

        # Converts the function result (dataframe) into a list, with blanks replaced by empty strings,
        # and compares it to the expected result.
        result = inventory_df.fillna('')
        result = [result.columns.tolist()] + result.values.tolist()
        expected = [column_names,
                    ['Share_A', 'FolderA1', 'Backlog', 'June', datetime(2122, 10, 15, 0, 0), '', '', ''],
                    ['Share_A', 'FolderA2', 'Backlog', 'June', datetime(2222, 10, 15, 0, 0), '', '', ''],
                    ['Share_B', 'FolderB', 'Backlog', 'June', datetime(2322, 10, 15, 0, 0), '', '', '']]
        self.assertEqual(result, expected, "Problem with test for dates, future")

    def test_strings_not_permanent(self):
        """Test for an inventory where the dates are a string but not 'permanent' or 'Permanent'"""
        column_names = ['Share (required)', 'Folder Name (required if not share)', 'Use Policy Category (required)',
                        'Person Responsible (required)', 'Date to review for deletion (required)',
                        'Additional information (optional)', 'Deleted (date) (optional)', 'Audit_Result']
        df = DataFrame([['Share_A', 'FolderA1', 'Backlog', 'June', '6 months', NaN, NaN, NaN],
                        ['Share_A', 'FolderA2', 'Backlog', 'June', 'year', NaN, NaN, NaN],
                        ['Share_B', 'FolderB', 'Backlog', 'June', 'In folder title', NaN, NaN, NaN]],
                       columns=column_names)
        inventory_df = check_dates(df)

        # Converts the function result (dataframe) into a list, with blanks replaced by empty strings,
        # and compares it to the expected result.
        result = inventory_df.fillna('')
        result = [result.columns.tolist()] + result.values.tolist()
        expected = [column_names,
                    ['Share_A', 'FolderA1', 'Backlog', 'June', '6 months', '', '', 'Check date'],
                    ['Share_A', 'FolderA2', 'Backlog', 'June', 'year', '', '', 'Check date'],
                    ['Share_B', 'FolderB', 'Backlog', 'June', 'In folder title', '', '', 'Check date']]
        self.assertEqual(result, expected, "Problem with test for strings, not permanent")

    def test_strings_permanent(self):
        """Test for an inventory where the dates are either 'permanent' or 'Permanent'"""

        # Makes a dataframe for function input, which would usually be made by read_inventory(), and runs the function.
        column_names = ['Share (required)', 'Folder Name (required if not share)', 'Use Policy Category (required)',
                        'Person Responsible (required)', 'Date to review for deletion (required)',
                        'Additional information (optional)', 'Deleted (date) (optional)', 'Audit_Result']
        df = DataFrame([['Share_A', 'FolderA1', 'Backlog', 'June', 'Permanent', NaN, NaN, NaN],
                        ['Share_A', 'FolderA2', 'Backlog', 'June', 'Permanent', NaN, NaN, NaN],
                        ['Share_B', 'FolderB', 'Backlog', 'June', 'permanent', NaN, NaN, NaN]],
                       columns=column_names)
        inventory_df = check_dates(df)

        # Converts the function result (dataframe) into a list, with blanks replaced by empty strings,
        # and compares it to the expected result.
        result = inventory_df.fillna('')
        result = [result.columns.tolist()] + result.values.tolist()
        expected = [column_names,
                    ['Share_A', 'FolderA1', 'Backlog', 'June', 'Permanent', '', '', ''],
                    ['Share_A', 'FolderA2', 'Backlog', 'June', 'Permanent', '', '', ''],
                    ['Share_B', 'FolderB', 'Backlog', 'June', 'permanent', '', '', '']]
        self.assertEqual(result, expected, "Problem with test for strings, permanent")


if __name__ == '__main__':
    unittest.main()
