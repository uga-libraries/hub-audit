"""
Tests for the script hub_audit.py
"""
import unittest
from datetime import date
from os import remove
from os.path import exists, join
from pandas import read_csv
from subprocess import CalledProcessError, PIPE, run


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
        result = run(f'python {script_path} "{inventory_path}" test_shares.csv', shell=True, stdout=PIPE)

        # Verifies the script printing the correct stats.
        printed = result.stdout.decode('utf-8')
        expected = 'Rows in the inventory (after cleanup): 19\r\n'
        self.assertEqual(printed, expected, 'Problem with test for printing stats')

        # Verifies the audit report was made.
        audit_report = join('inventories', f"digital_production_hub_audit_{date.today().strftime('%Y-%m')}.csv")
        self.assertEqual(exists(audit_report), True, 'Problem with test for audit report made')

        # Verifies the contents of the audit report are correct.
        df = read_csv(audit_report)
        df = df.fillna('nan')
        report_rows = [df.columns.tolist()] + df.values.tolist()
        expected = [['Share', 'Folder', 'Use', 'Responsible', 'Review_Date', 'Notes', 'Audit_Dates', 'Audit_Inventory', 'Audit_Required'],
                    ['A', 'Test Worksheet.xlsx', 'Working Files', 'Alex', '2024-01-01 00:00:00', 'nan', 'Expired', 'Correct', 'Correct'],
                    ['B', 'B', 'nan', 'nan', 'nan', 'nan', 'Review', 'Correct', 'Missing'],
                    ['C', 'C1', 'Backlog', 'Chris', '2124-03-18 00:00:00', 'nan', 'Correct', 'Correct', 'Correct'],
                    ['C', 'C2', 'Backlog', 'Chris', '2124-03-18 00:00:00', 'nan', 'Correct', 'Correct', 'Correct'],
                    ['C', 'C3', 'Backlog', 'Chris', '2124-03-18 00:00:00', 'nan', 'Correct', 'Not in share', 'Correct'],
                    ['C', 'C4', 'Backlog', 'Chris', '2124-03-18 00:00:00', 'nan', 'Correct', 'Not in share', 'Correct'],
                    ['C', 'Document.txt', 'Working Files', 'Camila', 'permanent', 'Documentation', 'Correct', 'Correct', 'Correct'],
                    ['Extra', 'E_1', 'Backlog', 'Erik', '2125-01-31 00:00:00', 'nan', 'Correct', 'Correct', 'Correct'],
                    ['Extra', 'E_2', 'Working Files', 'Erin', '2125-01-31 00:00:00', 'nan', 'Correct', 'Correct', 'Correct'],
                    ['Extra', 'E_3', 'nan', 'nan', 'nan', 'nan', 'nan', 'Not in inventory', 'nan'],
                    ['Extra', 'Text.txt', 'nan', 'nan', 'nan', 'nan', 'nan', 'Not in inventory', 'nan'],
                    ['Second_Level', 'S_1', 'Backlog', 'Sam', '2125-04-01 00:00:00', 'nan', 'Correct', 'Correct', 'Correct'],
                    ['Second_Level', 'S_2\\S_2a', 'Backlog', 'Sam', '2125-04-01 00:00:00', 'nan', 'Correct', 'Correct', 'Correct'],
                    ['Second_Level', 'S_2\\S_2b', 'Backlog', 'Sam', '2125-04-01 00:00:00', 'nan', 'Correct', 'Correct', 'Correct'],
                    ['Second_Level', 'S_3\\S_3a', 'Backlog', 'Sam', '2125-04-01 00:00:00', 'nan', 'Correct', 'Correct', 'Correct'],
                    ['Second_Level', 'S_3\\S_3b', 'Backlog', 'Sam', '2125-04-01 00:00:00', 'nan', 'Correct', 'Correct', 'Correct'],
                    ['Top', 'Include.txt', 'Transfer', 'Tina', '1 week', 'nan', 'Review', 'Correct', 'Correct'],
                    ['Top', 'T_1', 'Transfer', 'Tim', '2 months', 'nan', 'Review', 'Correct', 'Correct'],
                    ['Top', 'T_2', 'Transfer', 'Tina', '1 week', 'nan', 'Review', 'Correct', 'Correct'],
                    ['Top', 'T_Hub', 'Transfer', 'Tina', '1 week', 'nan', 'Review', 'Correct', 'Correct'],
                    ['mezz_one', 'mezz_one', 'Access/Mezzanine', 'Mike', 'Permanent', 'nan', 'Correct', 'Correct', 'Correct']]
        self.assertEqual(report_rows, expected, 'Problem with test for audit report contents')

    def test_error(self):
        """Test for when the script arguments are missing and the script exits"""
        script_path = join('..', 'hub_audit.py')

        # Runs the script without the required argument inventory and tests that it exits.
        with self.assertRaises(CalledProcessError):
            run(f'python {script_path}', shell=True, check=True, stdout=PIPE)

        # Runs the script again without the required argument inventory and tests it prints the correct error message.
        output = run(f'python {script_path}', shell=True, stdout=PIPE)
        error_msg = output.stdout.decode('utf-8')
        expected = 'Missing both required arguments, inventory and share information\r\n'
        self.assertEqual(error_msg, expected, 'Problem with test for error message')


if __name__ == '__main__':
    unittest.main()
