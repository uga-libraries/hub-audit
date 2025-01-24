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


def check_dates(df_inventory):
    """Find dates to review for deletion that are expired or need manual review

    A date needs manual review if it is text (e.g., 6 months) instead of a specific day,
    but not if it is "Permanent" or "permanent".

    @param
    df_inventory (pandas dataframe): data from the inventory

    @return
    df_inventory (pandas dataframe): data from inventory with updated Audit_Dates column
    """
    # For the portion of the dataframe where the date is a day,
    # updates Audit_Result if the date is earlier than today.
    df_date = df_inventory[(df_inventory['Review_Date'].apply(type) == datetime.datetime) | (df_inventory['Review_Date'].apply(type) == pd._libs.tslibs.timestamps.Timestamp)].copy()
    today = datetime.datetime.today()
    df_date.loc[df_date['Review_Date'] < today, 'Audit_Dates'] = 'Expired'

    # For the portion of the dataframe where the date is not a day (not datetime),
    # updates Audit_Result if it isn't 'permanent' (case-insensitive).
    df_nondate = df_inventory[(df_inventory['Review_Date'].apply(type) != datetime.datetime) & (df_inventory['Review_Date'].apply(type) != pd._libs.tslibs.timestamps.Timestamp)].copy()
    df_nondate.loc[df_nondate['Review_Date'].str.lower() != 'permanent', 'Audit_Dates'] = 'Review'

    # Recombines the dataframes with the updated Audit_Result column.
    df_inventory = pd.concat([df_date, df_nondate])
    df_inventory = df_inventory.sort_values(['Share', 'Folder'])

    # Updates the value of any cells that are still 'TBD' (have no errors) with "Correct".
    df_inventory.loc[df_inventory['Audit_Dates'] == 'TBD', 'Audit_Dates'] = 'Correct'

    return df_inventory


def check_inventory(df_inventory, df_shares):
    """Find folders in the share but not the inventory or in the inventory but not the share

    @param
    df_inventory (pandas dataframe): data from the inventory after cleanup
    df_shares (pandas dataframe): contents of all shares

    @return
    df_inventory (pandas dataframe): data from inventory updated with inventory match error
    Audit_Inventory column is updated for folders that are not in the share
    Folders are added to the dataframe if they are in the share but not the inventory
    """

    # Aligns with the original inventory dataframe with the shares dataframe.
    # Both the share and folder name need to be the same for a row to match in both dataframes.
    # indicator=True adds a new column, "_merge", which shows if the row was in one or both dataframes.
    df_inventory = df_inventory.merge(df_shares, on=['Share', 'Folder'], how='outer', indicator=True)

    # TODO: temp fix for error until I find the source
    df_inventory = df_inventory.drop_duplicates()

    # Updates the "Audit_Result" column for rows that are not in both shares.
    df_inventory.loc[df_inventory['_merge'] == 'left_only', 'Audit_Inventory'] = 'Not in share'
    df_inventory.loc[df_inventory['_merge'] == 'right_only', 'Audit_Inventory'] = 'Not in inventory'

    # Updates the value of any cells that are still blank (have no errors) with "Correct".
    df_inventory['Audit_Inventory'] = df_inventory['Audit_Inventory'].fillna('Correct')

    # Cleans up and returns the dataframe.
    # The temporary column '_merge' is removed and the rows are sorted.
    df_inventory = df_inventory.drop(['_merge'], axis=1)
    df_inventory = df_inventory.sort_values(['Share', 'Folder'])

    return df_inventory


def check_required(df_inventory):
    """Find blank cells in required columns

    @param
    df_inventory (pandas dataframe): data from the inventory after cleanup

    @return
    df_inventory (pandas dataframe): data from inventory with updated Audit_Required column
    """

    # List of required columns, after being renamed by the script.
    required = ['Share', 'Folder', 'Use', 'Responsible', 'Review_Date']

    # Find the blank cells in each of the required columns
    # and adds an error to the Audit_Required column.
    for column_name in required:
        df_inventory.loc[pd.isna(df_inventory[column_name]), 'Audit_Required'] = 'Missing'

    # Updates the value of any cells that are still TBD (have no errors) with "Correct".
    df_inventory.loc[df_inventory['Audit_Required'] == 'TBD', 'Audit_Required'] = 'Correct'

    return df_inventory


def make_shares_inventory(df_info):
    """Make a dataframe with the contents of all shares, to the level of detail specified in df_info

    @param
    df_info (pandas dataframe): data from the shares information csv

    @return
    df_shares (pandas dataframe): contents of all shares
    """

    # Makes an inventory of the contents of every share.
    share_inventory = {'Share': [], 'Folder': []}
    for share in df_info.itertuples():

        # Shares where the inventory just has the share name.
        if share.pattern == 'share':
            share_inventory['Share'].append(share.name)
            share_inventory['Folder'].append(share.name)

        # Shares where the inventory is just the top level folders.
        # Files are included unless they are .DS_Store or Hub documentation.
        elif share.pattern == 'top':
            for item in os.listdir(share.path):
                if os.path.isdir(os.path.join(share.path, item)) or (item != '.DS_Store' and 'Hub' not in item):
                    share_inventory['Share'].append(share.name)
                    share_inventory['Folder'].append(item)

        # Shares where the inventory includes second level folders for any top level folder in the folders list,
        # which is a pipe-separated string in df_shares.
        # Files are not included.
        elif share.pattern == 'second':
            for item in os.listdir(share.path):
                # Continue navigation if item is a directory and stop if it is a file.
                if os.path.isdir(os.path.join(share.path, item)):
                    for second_item in os.listdir(os.path.join(share.path, item)):
                        if os.path.isdir(os.path.join(share.path, item, second_item)):
                            if item in share.folders.split('|'):
                                # In born-digital folders, go to the third (collection) level in backlogged and closed:
                                if item.lower() == 'born-digital' and second_item in ('backlogged', 'closed'):
                                    for third_item in os.listdir(os.path.join(share.path, item, second_item)):
                                        if os.path.isdir(os.path.join(share.path, item, second_item, third_item)):
                                            share_inventory['Share'].append(share.name)
                                            share_inventory['Folder'].append(f'{item}\\{second_item}\\{third_item}')
                                else:
                                    share_inventory['Share'].append(share.name)
                                    share_inventory['Folder'].append(f'{item}\\{second_item}')
                            else:
                                share_inventory['Share'].append(share.name)
                                share_inventory['Folder'].append(item)
        # Catch shares with unexpected patterns.
        else:
            print('Error: config has an unexpected pattern', share.pattern)

    # Converts the share inventory to a dataframe.
    df_shares = pd.DataFrame.from_dict(share_inventory)
    return df_shares


def read_inventory(path):
    """Read inventory into dataframe, clean up, and add an Audit_Result column

    Clean up includes dropping unneeded rows and simplifying column names.

    @param
    path (string): path to the inventory, which is a script argument

    @return
    df (pandas dataframe): data from the inventory after cleanup
    """

    # Reads every sheet in the Excel spreadsheet, except for "Examples", into a single dataframe.
    sheet_dict = pd.read_excel(path, sheet_name=None)
    del sheet_dict['Examples']
    df_inventory = pd.concat(sheet_dict, ignore_index=True)

    # Removes the rows that describe each column
    # by keeping all rows except ones with the description in the first column.
    df_inventory = df_inventory[df_inventory['Share (required)'] != 'Name of the Hub share.']

    # Removes the rows of content that has been deleted
    # by keeping rows without information in the deleted date column.
    # Then it removes that column, which only has blanks remaining.
    df_inventory = df_inventory[df_inventory['Deleted (date) (optional)'].isnull()]
    df_inventory = df_inventory.drop(['Deleted (date) (optional)'], axis=1)

    # Removes blank rows.
    df_inventory = df_inventory.dropna(how='all')

    # Simplifies column names.
    df_inventory = df_inventory.rename({'Share (required)': 'Share',
                    'Folder Name (required if not share)': 'Folder',
                    'Use Policy Category (required)': 'Use',
                    'Person Responsible (required)': 'Responsible',
                    'Date to review for deletion (required)': 'Review_Date',
                    'Additional information (optional)': 'Notes'}, axis=1)

    # Adds new columns for recording errors found during the audit, one for each error type.
    # Initial values are TBD, so they can be updated with the results later without a dtype FutureWarning
    df_inventory['Audit_Dates'] = 'TBD'
    df_inventory['Audit_Inventory'] = 'TBD'
    df_inventory['Audit_Required'] = 'TBD'

    return df_inventory


if __name__ == '__main__':

    # Path to the Hub inventory and shares information csv (from the script arguments).
    # If either argument is missing or not a valid path, exits the script.
    inventory_path, shares_info_path, error_list = check_arguments(sys.argv)
    if len(error_list) > 0:
        for error in error_list:
            print(error)
        sys.exit(1)

    # Reads the inventory, a multiple sheet Excel spreadsheet, into one pandas dataframe, with cleanup.
    inventory_df = read_inventory(inventory_path)

    # Reads the share information into a dataframe.
    shares_info_df = pd.read_csv(shares_info_path)

    # Makes a dataframe with the folders in the shares, based on patterns in shares_info_df.
    shares_df = make_shares_inventory(shares_info_df)

    # Prints the number of rows in the inventory for the audit results spreadsheet.
    print("Rows in the inventory (after cleanup):", len(inventory_df.index))

    # Checks for blank cells in required columns.
    inventory_df = check_required(inventory_df)

    # Checks for dates to review for deletion that are expired or need manual review.
    inventory_df = check_dates(inventory_df)

    # Checks for mismatches between the inventory and Hub shares.
    inventory_df = check_inventory(inventory_df, shares_df)

    # Saves the inventory to a CSV for additional manual review.
    csv_path = os.path.join(os.path.dirname(inventory_path),
                            f"digital_production_hub_audit_{datetime.date.today().strftime('%Y-%m')}.csv")
    inventory_df.to_csv(csv_path, index=False)
