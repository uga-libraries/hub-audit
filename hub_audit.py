"""
Experiment into automating the majority of the analysis for the Digital Production Hub audit.
Required arguments: paths to the Digital Production Hub Inventory (Excel spreadsheet) and a CSV with share information.
"""
import datetime
import numpy as np
import os
import pandas as pd
import sys


def check_arguments(arg_list):
    """Check if the required arguments are present and valid paths

    @param
    arg_list (list): the contents of sys.argv after the script is run

    @return
    inventory (string, None): string with the path to the inventory, or None if error
    share_info (string, None): string with the path to the share information, or None if error
    errors (list): list with error messages, which is empty if there are no errors
    """

    # Variables for argument validation results.
    inventory = None
    share_info = None
    errors = []

    # Tests the arguments and updates the value of inventory or share_info if they are valid paths
    # and the errors list with each error found.
    if len(arg_list) == 1:
        errors.append('Missing both required arguments, inventory and share information')
    elif len(arg_list) == 2:
        errors.append('Missing one of the required arguments, inventory or share information')
    elif len(arg_list) == 3:
        if os.path.exists(arg_list[1]):
            inventory = arg_list[1]
        else:
            errors.append(f'Provided inventory "{arg_list[1]}" does not exist')
        if os.path.exists(arg_list[2]):
            share_info = arg_list[2]
        else:
            errors.append(f'Provided share information "{arg_list[2]}" does not exist')
    else:
        errors.append('Too many arguments. Should have two arguments, inventory and share information')

    return inventory, share_info, errors


def check_dates(df):
    """Find dates to review for deletion that are expired or need manual review

    A date needs manual review if it is text (e.g., 6 months) instead of a specific day,
    but not if it is "Permanent" or "permanent".

    @param
    df (pandas dataframe): data from the inventory

    @return
    df (pandas dataframe): data from inventory with updated Audit_Dates column
    """

    # For the portion of the dataframe where the date is a day,
    # updates Audit_Result if the date is earlier than today.
    df_date = df[df['Review_Date'].apply(type) == datetime.datetime].copy()
    today = datetime.datetime.today()
    df_date.loc[df_date['Review_Date'] < today, 'Audit_Dates'] = 'Expired'
    # print("date", df_date.shape)

    # For the portion of the dataframe where the date is not a day (not datetime),
    # updates Audit_Result if it isn't 'permanent' (case insensitive).
    df_nondate = df[df['Review_Date'].apply(type) != datetime.datetime].copy()
    df_nondate.loc[df_nondate['Review_Date'].str.lower() != 'permanent', 'Audit_Dates'] = 'Review'
    # print("nondate", df_nondate.shape)

    # Recombines the dataframes with the updated Audit_Result column.
    df = pd.concat([df_date, df_nondate])
    df = df.sort_values(['Share', 'Folder'])

    # Updates the value of any cells that are still blank (have no errors) with "Correct".
    df['Audit_Dates'] = df['Audit_Dates'].fillna('Correct')

    return df


def check_inventory(df, share_list):
    """Find folders in the share but not the inventory or in the inventory but not the share

    @param
    df (pandas dataframe): data from the inventory after cleanup
    shares (list): a list of dictionaries with data about each share: share name, path, inventory pattern,
                   and a list of second-level folders to include, which is empty if none are included

    @return
    df (pandas dataframe): data from inventory updated with inventory match error
    Audit_Inventory column is updated for folders that are not in the share
    Folders are added to the dataframe if they are in the share but not the inventory
    """

    # Makes an inventory of the contents of every share.
    share_inventory = {'Share': [], 'Folder': []}
    for share in share_list:
        share_name = share['name']

        # Shares where the inventory just has the share name.
        if share['pattern'] == 'share':
            share_inventory['Share'].append(share_name)
            share_inventory['Folder'].append(share_name)

        # Shares where the inventory is just the top level folders.
        elif share['pattern'] == 'top':
            for item in os.listdir(share['path']):
                share_inventory['Share'].append(share_name)
                share_inventory['Folder'].append(item)

        # Shares where the inventory includes second level folders for any top level folder in the folders list.
        elif share['pattern'] == 'second':
            for item in os.listdir(share['path']):
                if item in share['folders']:
                    for second_item in os.listdir(os.path.join(share['path'], item)):
                        share_inventory['Share'].append(share_name)
                        share_inventory['Folder'].append(f'{item}\\{second_item}')
                else:
                    share_inventory['Share'].append(share_name)
                    share_inventory['Folder'].append(item)

        # Catch shares with unexpected patterns.
        else:
            print(f'Error: config has an unexpected pattern')

    # Converts the share inventory to a dataframe and aligns with the original inventory dataframe.
    # Both the share and folder name need to be the same for a row to match in both dataframes.
    # indicator=True adds a new column, "_merge", which shows if the row was in one or both dataframes.
    share_df = pd.DataFrame.from_dict(share_inventory)
    df = df.merge(share_df, on=['Share', 'Folder'], how='outer', indicator=True)

    # Updates the "Audit_Result" column for rows that are not in both shares.
    df.loc[df['_merge'] == 'left_only', 'Audit_Inventory'] = 'Not in share'
    df.loc[df['_merge'] == 'right_only', 'Audit_Inventory'] = 'Not in inventory'

    # Updates the value of any cells that are still blank (have no errors) with "Correct".
    df['Audit_Inventory'] = df['Audit_Inventory'].fillna('Correct')

    # Cleans up and returns the dataframe.
    # The temporary column '_merge' is removed and the rows are sorted.
    df = df.drop(['_merge'], axis=1)
    df = df.sort_values(['Share', 'Folder'])

    return df


def check_required(df):
    """Find blank cells in required columns

    @param
    df (pandas dataframe): data from the inventory after cleanup

    @return
    df (pandas dataframe): data from inventory with updated Audit_Required column
    """

    # List of required columns, after being renamed by the script.
    required = ['Share', 'Folder', 'Use', 'Responsible', 'Review_Date']

    # Find the blank cells in each of the required columns
    # and adds an error to the Audit_Required column.
    for column_name in required:
        df.loc[pd.isna(df[column_name]), 'Audit_Required'] = 'Missing'

    # Updates the value of any cells that are still blank (have no errors) with "Correct".
    df['Audit_Required'] = df['Audit_Required'].fillna('Correct')

    return df


def hub_size():
    """Calculate the total size of all Hub shares in TB

    @param
    None

    @return
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
    """Read inventory into dataframe, clean up, and add an Audit_Result column

    Clean up includes dropping unneeded rows and simplifying column names.

    @param
    path (string): path to the inventory, which is a script argument

    @return
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

    # Simplifies column names.
    df = df.rename({'Share (required)': 'Share',
                    'Folder Name (required if not share)': 'Folder',
                    'Use Policy Category (required)': 'Use',
                    'Person Responsible (required)': 'Responsible',
                    'Date to review for deletion (required)': 'Review_Date',
                    'Additional information (optional)': 'Notes',
                    'Deleted (date) (optional)': 'Deleted_Date'}, axis=1)

    # Adds new columns for recording errors found during the audit, one for each error type.
    df['Audit_Dates'] = np.nan
    df['Audit_Inventory'] = np.nan
    df['Audit_Required'] = np.nan

    return df


if __name__ == '__main__':

    # Path to the Hub inventory and shares information csv (from the script arguments).
    # If either argument is missing or not a valid path, exits the script.
    inventory_path, shares_path, error = check_argument(sys.argv)
    if len(error_list) > 0:
        for error in error_list:
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

    # Checks for dates to review for deletion that are expired or need manual review.
    inventory_df = check_dates(inventory_df)

    # Checks for mismatches between the inventory and Hub shares.
    shares_df = pd.read_csv(shares_path)
    inventory_df = check_inventory(inventory_df, shares_df)

    # Saves the inventory to a CSV for additional manual review.
    csv_path = os.path.join(os.path.dirname(inventory_path),
                            f"digital_production_hub_audit_{datetime.date.today().strftime('%Y-%m')}.csv")
    inventory_df.to_csv(csv_path, index=False)
