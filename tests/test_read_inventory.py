"""
Tests for the function read_inventory(), which reads data from Excel to a dataframe and cleans it up.
"""
import unittest
from hub_audit import read_inventory
from datetime import datetime
from os.path import join


class MyTestCase(unittest.TestCase):

    def test_blank_rows(self):
        """Test for an inventory with blank rows
        Includes a share with no blank (mezzanine_1), some blank (digital_ingest), and all blank (russell)"""
        inventory_path = join('inventories', 'Digital Production Hub Inventory_Blank Rows.xlsx')
        inventory_df = read_inventory(inventory_path)

        result = inventory_df.fillna('')
        result = [result.columns.tolist()] + result.values.tolist()
        expected = [['Share', 'Folder', 'Use', 'Responsible', 'Review_Date', 'Notes',
                     'Audit_Dates', 'Audit_Inventory', 'Audit_Required'],
                    ['digital_ingest', 'alston01', 'Backlog', 'Callie', datetime(2023, 9, 30), '', '', '', ''],
                    ['digital_ingest', 'alston03', 'Backlog', 'Callie', datetime(2023, 9, 30), '', '', '', ''],
                    ['mezzanine_1', 'mezzanine_1', 'Access/Mezzanine', 'Callie', 'permanent', '', '', '', '']]
        self.assertEqual(result, expected, "Problem with test for blank rows")

    def test_deletions(self):
        """Test for an inventory with rows for content that has been deleted
        Includes a share with none deleted (DLG_TWO), some deleted (Dig Stew), and all deleted (SCL_Imaging_Lab)"""
        inventory_path = join('inventories', 'Digital Production Hub Inventory_Deletions.xlsx')
        inventory_df = read_inventory(inventory_path)

        result = inventory_df.fillna('')
        result = [result.columns.tolist()] + result.values.tolist()
        expected = [['Share', 'Folder', 'Use', 'Responsible', 'Review_Date', 'Notes',
                     'Audit_Dates', 'Audit_Inventory', 'Audit_Required'],
                    ['Dig Stew', 'AIT\\2024-02', 'Backlog', 'Adriane', '3 months', '', '', '', ''],
                    ['Dig Stew', 'Topic_Modeling', 'Working Files', 'Adriane', datetime(2025, 1, 31), '', '', '', ''],
                    ['DLG_TWO', 'curation\\athens', 'Backlog', 'Donnie', datetime(2024, 8, 3, 0, 0), '', '', '', ''],
                    ['DLG_TWO', 'curation\\atlanta', 'Backlog', 'Donnie', datetime(2024, 8, 10, 0, 0), '', '', '', '']]
        self.assertEqual(result, expected, "Problem with test for deletions")

    def test_usual(self):
        """Test for an inventory with the usual data"""
        inventory_path = join('inventories', 'Digital Production Hub Inventory_Usual.xlsx')
        inventory_df = read_inventory(inventory_path)

        result = inventory_df.fillna('')
        result = [result.columns.tolist()] + result.values.tolist()
        expected = [['Share', 'Folder', 'Use', 'Responsible', 'Review_Date', 'Notes',
                     'Audit_Dates', 'Audit_Inventory', 'Audit_Required'],
                    ['Hargrett', 'Access\\ms1234', 'Access/Mezzanine',  'Emmeline', 'Permanent', 'Redacted', '', '', ''],
                    ['Hargrett', 'Access\\Kiosk', 'Access/Mezzanine', 'Emmeline', 'Permanent', '', '', '', ''],
                    ['Hargrett', 'Oral history temp', 'Transfer', 'Steve', '6 months after creation', '', '', '', ''],
                    ['MAGIL_GGP', 'Legislative docs', 'Transfer', 'Sarah', datetime(2024, 7, 1,0, 0), 'Pilot', '', '', ''],
                    ['SCL_Imaging_Lab', 'backlog', 'Backlog', 'Chris', datetime(2024, 6, 1, 0, 0), '', '', '', ''],
                    ['SCL_Imaging_Lab', 'tiffs', 'Medium Priority', 'Mary', 'Permanent', '', '', '', '']]
        self.assertEqual(result, expected, "Problem with test for usual")


if __name__ == '__main__':
    unittest.main()
