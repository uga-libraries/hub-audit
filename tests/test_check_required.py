"""
Tests for the function check_required, which finds missing values in required columns
"""
import unittest
from hub_audit import check_required
from numpy import NaN
from pandas import DataFrame


class MyTestCase(unittest.TestCase):

    def test_complete(self):
        """Test for an inventory with data in all required columns"""
        column_names = ['Share (required)', 'Folder Name (required if not share)', 'Use Policy Category (required)',
                        'Person Responsible (required)', 'Date to review for deletion (required)',
                        'Additional information (optional)', 'Deleted (date) (optional)', 'Audit_Result']
        df = DataFrame([['Share_One', 'Folder1', 'Medium Priority', 'Bill', 'Permanent', NaN, NaN, NaN],
                        ['Share_One', 'Folder2', 'Medium Priority', 'Bill', 'Permanent', NaN, NaN, NaN],
                        ['Share_One', 'Folder3', 'Medium Priority', 'Bill', 'Permanent', NaN, NaN, NaN]],
                       columns=column_names)
        inventory_df = check_required(df)

        result = inventory_df.fillna('')
        result = [result.columns.tolist()] + result.values.tolist()
        expected = [column_names,
                    ['Share_One', 'Folder1', 'Medium Priority', 'Bill', 'Permanent', '', '', ''],
                    ['Share_One', 'Folder2', 'Medium Priority', 'Bill', 'Permanent', '', '', ''],
                    ['Share_One', 'Folder3', 'Medium Priority', 'Bill', 'Permanent', '', '', '']]
        self.assertEqual(result, expected, "Problem with test for complete data")

    def test_missing_combination(self):
        """Test for an inventory missing data in multiple required columns"""
        column_names = ['Share (required)', 'Folder Name (required if not share)', 'Use Policy Category (required)',
                        'Person Responsible (required)', 'Date to review for deletion (required)',
                        'Additional information (optional)', 'Deleted (date) (optional)', 'Audit_Result']
        df = DataFrame([[NaN, NaN, 'Medium Priority', NaN, 'Permanent', NaN, NaN, NaN],
                        [NaN, NaN, NaN, NaN, NaN, 'Note', NaN, NaN],
                        ['Share_One', 'Folder3', NaN, 'Bill', NaN, NaN, NaN, NaN]],
                       columns=column_names)
        inventory_df = check_required(df)

        result = inventory_df.fillna('')
        result = [result.columns.tolist()] + result.values.tolist()
        expected = [column_names,
                    ['', '', 'Medium Priority', '', 'Permanent', '', '', 'Missing required data'],
                    ['', '', '', '', '', 'Note', '', 'Missing required data'],
                    ['Share_One', 'Folder3', '', 'Bill', '', '', '', 'Missing required data']]
        self.assertEqual(result, expected, "Problem with test for missing combinations of required columns")

    def test_missing_date(self):
        """Test for an inventory missing data in the "Date to review for deletion" column"""
        column_names = ['Share (required)', 'Folder Name (required if not share)', 'Use Policy Category (required)',
                        'Person Responsible (required)', 'Date to review for deletion (required)',
                        'Additional information (optional)', 'Deleted (date) (optional)', 'Audit_Result']
        df = DataFrame([['Share_One', 'Folder1', 'Medium Priority', 'Bill', NaN, NaN, NaN, NaN],
                        ['Share_One', 'Folder2', 'Medium Priority', 'Bill', NaN, NaN, NaN, NaN],
                        ['Share_One', 'Folder3', 'Medium Priority', 'Bill', 'Permanent', NaN, NaN, NaN]],
                       columns=column_names)
        inventory_df = check_required(df)

        result = inventory_df.fillna('')
        result = [result.columns.tolist()] + result.values.tolist()
        expected = [column_names,
                    ['Share_One', 'Folder1', 'Medium Priority', 'Bill', '', '', '', 'Missing required data'],
                    ['Share_One', 'Folder2', 'Medium Priority', 'Bill', '', '', '', 'Missing required data'],
                    ['Share_One', 'Folder3', 'Medium Priority', 'Bill', 'Permanent', '', '', '']]
        self.assertEqual(result, expected, "Problem with test for missing date to review for deletion")

    def test_missing_folder(self):
        """Test for an inventory missing data in the "Folder Name" column"""
        column_names = ['Share (required)', 'Folder Name (required if not share)', 'Use Policy Category (required)',
                        'Person Responsible (required)', 'Date to review for deletion (required)',
                        'Additional information (optional)', 'Deleted (date) (optional)', 'Audit_Result']
        df = DataFrame([['Share_One', 'Folder1', 'Medium Priority', 'Bill', 'Permanent', NaN, NaN, NaN],
                        ['Share_One', NaN, 'Medium Priority', 'Bill', 'Permanent', NaN, NaN, NaN],
                        ['Share_One', NaN, 'Medium Priority', 'Bill', 'Permanent', NaN, NaN, NaN]],
                       columns=column_names)
        inventory_df = check_required(df)

        result = inventory_df.fillna('')
        result = [result.columns.tolist()] + result.values.tolist()
        expected = [column_names,
                    ['Share_One', 'Folder1', 'Medium Priority', 'Bill', 'Permanent', '', '', ''],
                    ['Share_One', '', 'Medium Priority', 'Bill', 'Permanent', '', '', 'Missing required data'],
                    ['Share_One', '', 'Medium Priority', 'Bill', 'Permanent', '', '', 'Missing required data']]
        self.assertEqual(result, expected, "Problem with test for missing folder name")

    def test_missing_person(self):
        """Test for an inventory missing data in the "Person Responsible" column"""
        column_names = ['Share (required)', 'Folder Name (required if not share)', 'Use Policy Category (required)',
                        'Person Responsible (required)', 'Date to review for deletion (required)',
                        'Additional information (optional)', 'Deleted (date) (optional)', 'Audit_Result']
        df = DataFrame([['Share_One', 'Folder1', 'Medium Priority', NaN, 'Permanent', NaN, NaN, NaN],
                        ['Share_One', 'Folder2', 'Medium Priority', NaN, 'Permanent', NaN, NaN, NaN],
                        ['Share_One', 'Folder3', 'Medium Priority', NaN, 'Permanent', NaN, NaN, NaN]],
                       columns=column_names)
        inventory_df = check_required(df)

        result = inventory_df.fillna('')
        result = [result.columns.tolist()] + result.values.tolist()
        expected = [column_names,
                    ['Share_One', 'Folder1', 'Medium Priority', '', 'Permanent', '', '', 'Missing required data'],
                    ['Share_One', 'Folder2', 'Medium Priority', '', 'Permanent', '', '', 'Missing required data'],
                    ['Share_One', 'Folder3', 'Medium Priority', '', 'Permanent', '', '', 'Missing required data']]
        self.assertEqual(result, expected, "Problem with test for missing person responsible")

    def test_missing_share(self):
        """Test for an inventory missing data in the "Share" column"""
        column_names = ['Share (required)', 'Folder Name (required if not share)', 'Use Policy Category (required)',
                        'Person Responsible (required)', 'Date to review for deletion (required)',
                        'Additional information (optional)', 'Deleted (date) (optional)', 'Audit_Result']
        df = DataFrame([[NaN, 'Folder1', 'Medium Priority', 'Bill', 'Permanent', NaN, NaN, NaN],
                        ['Share_One', 'Folder2', 'Medium Priority', 'Bill', 'Permanent', NaN, NaN, NaN],
                        [NaN, 'Folder3', 'Medium Priority', 'Bill', 'Permanent', NaN, NaN, NaN]],
                       columns=column_names)
        inventory_df = check_required(df)

        result = inventory_df.fillna('')
        result = [result.columns.tolist()] + result.values.tolist()
        expected = [column_names,
                    ['', 'Folder1', 'Medium Priority', 'Bill', 'Permanent', '', '', 'Missing required data'],
                    ['Share_One', 'Folder2', 'Medium Priority', 'Bill', 'Permanent', '', '', ''],
                    ['', 'Folder3', 'Medium Priority', 'Bill', 'Permanent', '', '', 'Missing required data']]
        self.assertEqual(result, expected, "Problem with test for missing share")

    def test_missing_use(self):
        """Test for an inventory missing data in the "Use Policy Category" column"""
        column_names = ['Share (required)', 'Folder Name (required if not share)', 'Use Policy Category (required)',
                        'Person Responsible (required)', 'Date to review for deletion (required)',
                        'Additional information (optional)', 'Deleted (date) (optional)', 'Audit_Result']
        df = DataFrame([['Share_One', 'Folder1', 'Medium Priority', 'Bill', 'Permanent', NaN, NaN, NaN],
                        ['Share_One', 'Folder2', 'Medium Priority', 'Bill', 'Permanent', NaN, NaN, NaN],
                        ['Share_One', 'Folder3', NaN, 'Bill', 'Permanent', NaN, NaN, NaN]],
                       columns=column_names)
        inventory_df = check_required(df)

        result = inventory_df.fillna('')
        result = [result.columns.tolist()] + result.values.tolist()
        expected = [column_names,
                    ['Share_One', 'Folder1', 'Medium Priority', 'Bill', 'Permanent', '', '', ''],
                    ['Share_One', 'Folder2', 'Medium Priority', 'Bill', 'Permanent', '', '', ''],
                    ['Share_One', 'Folder3', '', 'Bill', 'Permanent', '', '', 'Missing required data']]
        self.assertEqual(result, expected, "Problem with test for missing use policy category")


if __name__ == '__main__':
    unittest.main()
