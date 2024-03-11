"""
Experiment into automating the majority of the analysis for the Digital Production Hub audit
"""
import datetime
import os
import pandas as pd
import sys


def check_argument(arg_list):
    """Check if the required argument is present and a valid path

    :parameter
    arg_list (list): the contents of sys.argv after the script is run

    :returns
    inventory (string, None): string with the path to the inventory, or None if error
    error (string, None): string with the error message, or None if no error
    """

    # Verifies the required argument (inventory) is present and a valid path.
    # If the number of arguments is incorrect, inventory_path is set to None.
    # If there is no error, error is set to None.
    if len(arg_list) == 1:
        return None, 'Missing required argument: inventory'
    elif len(arg_list) == 2:
        inventory = arg_list[1]
        if os.path.exists(inventory):
            return inventory, None
        else:
            return None, f'Provided inventory "{inventory}" does not exist'
    else:
        return None, 'Too many arguments. Should just have one argument, inventory'


def check_dates(df):
    """Find deletion dates that are expired or need manual review and add to Audit_result column

    :parameter
    df (pandas dataframe): data from the inventory after cleanup

    :returns
    df (pandas dataframe): data from inventory with updated Audit_Result column
    """
    # Finds any dates that are earlier than the current date.
    today = datetime.datetime.today()
    column = 'Date to review for deletion (required)'

    df.loc[(df[column].apply(type) == datetime.datetime) & (df[column] < today), 'Audit_Result'] = 'Date expired'

    # Finds any non-dates that are not "Permanent" or "Permanent" to flag for manual review.
    df.loc[(df[column].apply(type) == str) & (df[column].str.lower() != 'permanent'), 'Audit_Result'] = 'Check date'

    return df


def check_required(df):
    """Find blank cells in required columns and add error to Audit_Result column

    :parameter
    df (pandas dataframe): data from the inventory after cleanup

    :returns
    df (pandas dataframe): data from inventory with updated Audit_Result column
    """
    # List of required columns.
    required = ['Share (required)', 'Folder Name (required if not share)', 'Use Policy Category (required)',
                'Person Responsible (required)', 'Date to review for deletion (required)']

    # Find the blank cells in each of the required columns
    # and add that information to the Audit_Result column.
    for column_name in required:
        df.loc[pd.isna(df[column_name]), 'Audit_Result'] = 'Missing required data'

    return df


def hub_size():
    """Calculate the total size of all Hub shares in TB

    :parameter
    None

    :returns
    total (float): combined sizes of all Hub shares in TB
    """

    # For testing, a list of shares to include, which are in this repo.
    # For production, may import from a configuration file.
    shares = [os.path.join('shares', 'A'), os.path.join('shares', 'B'), os.path.join('shares', 'C')]

    # Adds the size of each share to the total.
    total_bytes = 0
    for share in shares:
        for root, dirs, files in os.walk(share):
            for file in files:
                file_path = os.path.join(root, file)
                total_bytes += os.path.getsize(file_path)

    # For testing, converts the size to MB and round to 2 decimals.
    # In production, plan to convert to a TB round to a whole number.
    total_mb = round(total_bytes/1000000, 2)
    return total_mb


def read_inventory(path):
    """Read inventory into dataframe, drop unneeded rows, and add an Audit_Result column

    :parameter
    path (string): path to the inventory, which is a script argument

    :returns
    df (pandas dataframe): data from the inventory after cleanup
    """
    # Reads every sheet in the Excel spreadsheet into a single dataframe.
    df = pd.concat(pd.read_excel(path, sheet_name=None), ignore_index=True)

    # Removes the rows that describe each column
    # by keeping all rows except ones with the description in the first column.
    df = df[df['Share (required)'] != 'Name of the Hub share.']

    # Removes the rows of content that has been deleted
    # by keeping rows without information in the deleted date column.
    df = df[df['Deleted (date) (optional)'].isnull()]

    # Removes blank rows.
    df = df.dropna(how='all')

    # Adds a new column for recording errors.
    df['Audit_Result'] = ''

    return df


if __name__ == '__main__':

    # Path to the inventory (from the script argument).
    # If the argument is missing or not a valid path, exits the script.
    inventory_path, error = check_argument(sys.argv)
    if error:
        print(error)
        sys.exit(1)

    # Reads the inventory, a multiple sheet Excel spreadsheet, into one pandas dataframe, with cleanup.
    inventory_df = read_inventory(inventory_path)

    # Prints statistics (number of rows in the inventory and TB in all shares) for the audit results spreadsheet.
    print("Rows in the inventory (after cleanup):", len(inventory_df.index))
    size = hub_size()
    print("Size of shares in TB:", size)

    # Checks for blank cells in required columns.
    inventory_df = check_required(inventory_df)

    # Checks for dates to review for deletion that are expired or need manual review
    inventory_df = check_dates(inventory_df)