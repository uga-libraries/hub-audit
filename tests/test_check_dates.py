"""
Tests for the function check_dates(), which finds dates to review for deletion that have expired.

For easier testing, the dataframe with inventory data is made within the function using pandas.
In production, it is made by reading an Excel spreadsheet using read_inventory().
"""
import unittest
from hub_audit import check_dates
from datetime import datetime
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
        self.columns = ['Share', 'Folder', 'Use', 'Responsible', 'Review_Date', 'Notes', 'Deleted_Date', 'Audit_Result']

    def test_combination(self):
        """Test for an inventory where the date formatting is mixed"""
        # Make a dataframe with Hub inventory data and run the function being tested.
        rows = [['Share_A', 'A1', 'Backlog', 'June', 'Permanent', NaN, NaN, NaN],
                ['Share_A', 'A2', 'Backlog', 'June', datetime(2021, 1, 1, 0, 0), NaN, NaN, NaN],
                ['Share_B', 'B', 'Backlog', 'June', '6 months', NaN, NaN, NaN],
                ['Share_C', 'C1', 'Backlog', 'June', datetime(3031, 12, 14, 0, 0), NaN, NaN, NaN],
                ['Share_C', 'C2', 'Backlog', 'June', 'permanent', NaN, NaN, NaN]]
        inventory_df = check_dates(DataFrame(rows, columns=self.columns))

        # Tests if the resulting dataframe has the expected data.
        result = df_to_list(inventory_df)
        expected = [self.columns,
                    ['Share_A', 'A1', 'Backlog', 'June', 'Permanent', 'nan', 'nan', 'nan'],
                    ['Share_A', 'A2', 'Backlog', 'June', datetime(2021, 1, 1, 0, 0), 'nan', 'nan', 'Date expired'],
                    ['Share_B', 'B', 'Backlog', 'June', '6 months', 'nan', 'nan', 'Check date'],
                    ['Share_C', 'C1', 'Backlog', 'June', datetime(3031, 12, 14, 0, 0), 'nan', 'nan', 'nan'],
                    ['Share_C', 'C2', 'Backlog', 'June', 'permanent', 'nan', 'nan', 'nan']]
        self.assertEqual(result, expected, "Problem with test for combined date formats")

    def test_dates_expired(self):
        """Test for an inventory where the dates are formatted as a date and the dates are in the past"""
        # Make a dataframe with Hub inventory data and run the function being tested.
        rows = [['Share_A', 'A1', 'Backlog', 'June', datetime(2022, 10, 15, 0, 0), NaN, NaN, NaN],
                ['Share_A', 'A2', 'Backlog', 'June', datetime(2021, 10, 15, 0, 0), NaN, NaN, NaN],
                ['Share_B', 'B', 'Backlog', 'June', datetime(2020, 10, 15, 0, 0), NaN, NaN, NaN]]
        inventory_df = check_dates(DataFrame(rows, columns=self.columns))

        # Tests if the resulting dataframe has the expected data.
        result = df_to_list(inventory_df)
        expected = [self.columns,
                    ['Share_A', 'A1', 'Backlog', 'June', datetime(2022, 10, 15, 0, 0), 'nan', 'nan', 'nan'],
                    ['Share_A', 'A2', 'Backlog', 'June', datetime(2021, 10, 15, 0, 0), 'nan', 'nan', 'nan'],
                    ['Share_B', 'B', 'Backlog', 'June', datetime(2020, 10, 15, 0, 0), 'nan', 'nan', 'nan']]
        self.assertEqual(result, expected, "Problem with test for dates, expired")

    def test_dates_future(self):
        """Test for an inventory where the dates are formatted as a date and the dates are in the future"""
        # Make a dataframe with Hub inventory data and run the function being tested.
        rows = [['Share_A', 'A1', 'Backlog', 'June', datetime(2122, 10, 15, 0, 0), NaN, NaN, NaN],
                ['Share_A', 'A2', 'Backlog', 'June', datetime(2222, 10, 15, 0, 0), NaN, NaN, NaN],
                ['Share_B', 'B', 'Backlog', 'June', datetime(2322, 10, 15, 0, 0), NaN, NaN, NaN]]
        inventory_df = check_dates(DataFrame(rows, columns=self.columns))

        # Tests if the resulting dataframe has the expected data.
        result = df_to_list(inventory_df)
        expected = [self.columns,
                    ['Share_A', 'A1', 'Backlog', 'June', datetime(2122, 10, 15, 0, 0), 'nan', 'nan', 'nan'],
                    ['Share_A', 'A2', 'Backlog', 'June', datetime(2222, 10, 15, 0, 0), 'nan', 'nan', 'nan'],
                    ['Share_B', 'B', 'Backlog', 'June', datetime(2322, 10, 15, 0, 0), 'nan', 'nan', 'nan']]
        self.assertEqual(result, expected, "Problem with test for dates, future")

    def test_strings_not_permanent(self):
        """Test for an inventory where the dates are a string but not 'permanent' or 'Permanent'"""
        # Make a dataframe with Hub inventory data and run the function being tested.
        rows = [['Share_A', 'A1', 'Backlog', 'June', '6 months', NaN, NaN, NaN],
                ['Share_A', 'A2', 'Backlog', 'June', 'year', NaN, NaN, NaN],
                ['Share_B', 'B', 'Backlog', 'June', 'In folder title', NaN, NaN, NaN]]
        inventory_df = check_dates(DataFrame(rows, columns=self.columns))

        # Tests if the resulting dataframe has the expected data.
        result = df_to_list(inventory_df)
        expected = [self.columns,
                    ['Share_A', 'A1', 'Backlog', 'June', '6 months', 'nan', 'nan', 'Check date'],
                    ['Share_A', 'A2', 'Backlog', 'June', 'year', 'nan', 'nan', 'Check date'],
                    ['Share_B', 'B', 'Backlog', 'June', 'In folder title', 'nan', 'nan', 'Check date']]
        self.assertEqual(result, expected, "Problem with test for strings, not permanent")

    def test_strings_permanent(self):
        """Test for an inventory where the dates are either 'permanent' or 'Permanent'"""
        # Make a dataframe with Hub inventory data and run the function being tested.
        rows = [['Share_A', 'A1', 'Backlog', 'June', 'Permanent', NaN, NaN, NaN],
                ['Share_A', 'A2', 'Backlog', 'June', 'Permanent', NaN, NaN, NaN],
                ['Share_B', 'B', 'Backlog', 'June', 'permanent', NaN, NaN, NaN]]
        inventory_df = check_dates(DataFrame(rows, columns=self.columns))

        # Tests if the resulting dataframe has the expected data.
        result = df_to_list(inventory_df)
        expected = [self.columns,
                    ['Share_A', 'A1', 'Backlog', 'June', 'Permanent', 'nan', 'nan', 'nan'],
                    ['Share_A', 'A2', 'Backlog', 'June', 'Permanent', 'nan', 'nan', 'nan'],
                    ['Share_B', 'B', 'Backlog', 'June', 'permanent', 'nan', 'nan', 'nan']]
        self.assertEqual(result, expected, "Problem with test for strings, permanent")


if __name__ == '__main__':
    unittest.main()
