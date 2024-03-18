"""
Tests for the script hub_audit.py
"""
import unittest
from datetime import date
from os import remove
from os.path import exists, join
from pandas import read_csv
from subprocess import PIPE, run


class MyTestCase(unittest.TestCase):

    def tearDown(self):
        """Delete the audit report, if made"""
        audit_report = join('inventories', f"digital_production_hub_audit_{date.today().strftime('%Y-%m')}.csv")
        if exists(audit_report):
            remove(audit_report)

    def test_correct(self):
        """Test for when the script runs correctly on all folder sin tests/shares."""
        script_path = join('..', 'hub_audit.py')
        inventory_path = join('inventories', 'Digital Production Hub Inventory.xlsx')
        result = run(f'python {script_path} "{inventory_path}"', shell=True, stdout=PIPE)

        # Verifies the script printing the correct stats.
        printed = result.stdout.decode('utf-8')
        expected = 'Rows in the inventory (after cleanup): 17\r\n' \
                   'Size of shares in TB: 0.15\r\n'
        self.assertEqual(printed, expected, 'Problem with test for printing stats')

        # Verifies the audit report was made.
        audit_report = join('inventories', f"digital_production_hub_audit_{date.today().strftime('%Y-%m')}.csv")
        self.assertEqual(exists(audit_report), True, 'Problem with test for audit report made')

        # Verifies the contents of the audit report are correct.
        df = read_csv(audit_report)
        df = df.fillna('nan')
        report_rows = [df.columns.tolist()] + df.values.tolist()
        expected = [['Share', 'Folder', 'Use', 'Responsible', 'Review_Date', 'Notes', 'Deleted_Date', 'Audit_Result'],
                    ['A', 'Test Worksheet.xlsx', 'Working Files', 'Alex', '2024-01-01 00:00:00', 'nan', 'nan', 'Date expired'],
                    ['B', 'B', 'nan', 'nan', 'permanent', 'nan', 'nan', 'Missing required data'],
                    ['C', 'C1', 'Backlog', 'Chris', '2124-03-18 00:00:00', 'nan', 'nan', 'Correct'],
                    ['C', 'C2', 'Backlog', 'Chris', '2124-03-18 00:00:00', 'nan', 'nan', 'Correct'],
                    ['C', 'C3', 'Backlog', 'Chris', '2124-03-18 00:00:00', 'nan', 'nan', 'Not in share'],
                    ['C', 'C4', 'Backlog', 'Chris', '2124-03-18 00:00:00', 'nan', 'nan', 'Not in share'],
                    ['C', 'Document.txt', 'Working Files', 'Camila', 'permanent', 'Documentation', 'nan', 'Correct'],
                    ['Extra', 'E_1', 'Backlog', 'Erik', '2125-01-31 00:00:00', 'nan', 'nan', 'Correct'],
                    ['Extra', 'E_2', 'Working Files', 'Erin', '2125-01-31 00:00:00', 'nan', 'nan', 'Correct'],
                    ['Extra', 'E_3', 'nan', 'nan', 'nan', 'nan', 'nan', 'Not in inventory'],
                    ['Extra', 'Text.txt', 'nan', 'nan', 'nan', 'nan', 'nan', 'Not in inventory'],
                    ['Second_Level', 'S_1', 'Backlog', 'Sam', '2125-04-01 00:00:00', 'nan', 'nan', 'Correct'],
                    ['Second_Level', 'S_2\\S_2a', 'Backlog', 'Sam', '2125-04-01 00:00:00', 'nan', 'nan', 'Correct'],
                    ['Second_Level', 'S_2\\S_2b', 'Backlog', 'Sam', '2125-04-01 00:00:00', 'nan', 'nan', 'Correct'],
                    ['Second_Level', 'S_3\\S_3a', 'Backlog', 'Sam', '2125-04-01 00:00:00', 'nan', 'nan', 'Correct'],
                    ['Second_Level', 'S_3\\S_3b', 'Backlog', 'Sam', '2125-04-01 00:00:00', 'nan', 'nan', 'Correct'],
                    ['Top', 'T_1', 'Transfer', 'Tim', '2 months', 'nan', 'nan', 'Check date'],
                    ['Top', 'T_2', 'Transfer', 'Tina', '1 week', 'nan', 'nan', 'Check date'],
                    ['mezz_one', 'mezz_one', 'Access/Mezzanine', 'Mike', 'Permanent', 'nan', 'nan', 'Correct']]
        self.assertEqual(report_rows, expected, 'Problem with test for audit report contents')


if __name__ == '__main__':
    unittest.main()
