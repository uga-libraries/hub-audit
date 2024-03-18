"""
Experiment into automating the majority of the analysis for the Digital Production Hub audit.
Required argument: path to the Digital Production Hub Inventory (Excel spreadsheet)
"""
import datetime
import os
import pandas as pd
import sys
from config import shares


def check_argument(arg_list):
    """Check if the required argument is present and a valid path

    @param
    arg_list (list): the contents of sys.argv after the script is run

    @return
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
    """Find dates to review for deletion that are expired or need manual review

    A date needs manual review if it is text (e.g., 6 months) instead of a specific day,
    but not if it is "Permanent" or "permanent".

    @param
    df (pandas dataframe): data from the inventory

    @return
    df (pandas dataframe): data from inventory with updated Audit_Result column
    """

    # For the portion of the dataframe where the date is a day,
    # updates Audit_Result if the date is earlier than today.
    df_date = df[df['Review_Date'].apply(type) == datetime.datetime].copy()
    today = datetime.datetime.today()
    df_date.loc[df_date['Review_Date'] < today, 'Audit_Result'] = 'Date expired'
    # print("date", df_date.shape)

    # For the portion of the dataframe where the date is not a day (not datetime),
    # updates Audit_Result if it isn't 'permanent' (case insensitive).
    df_nondate = df[df['Review_Date'].apply(type) != datetime.datetime].copy()
    df_nondate.loc[df_nondate['Review_Date'].str.lower() != 'permanent', 'Audit_Result'] = 'Check date'
    # print("nondate", df_nondate.shape)

    # Recombines the dataframes with the updated Audit_Result column.
    df = pd.concat([df_date, df_nondate])
    df = df.sort_values(['Share', 'Folder'])
    return df


def check_inventory(df, share_list):
    """Find folders in the share but not the inventory or in the inventory but not the share

    @param
    df (pandas dataframe): data from the inventory after cleanup
    shares (list): a list of dictionaries with data about each share: share name, path, inventory pattern,
                   and a list of second-level folders to include, which is empty if none are included

    @return
    df (pandas dataframe): data from inventory updated with inventory match error
    Audit_Result column is updated for folders that are not in the share
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
    df.loc[df['_merge'] == 'left_only', 'Audit_Result'] = 'Not in share'
    df.loc[df['_merge'] == 'right_only', 'Audit_Result'] = 'Not in inventory'

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
    df (pandas dataframe): data from inventory with updated Audit_Result column
    """

    # List of required columns, after being renamed by the script.
    required = ['Share', 'Folder', 'Use', 'Responsible', 'Review_Date']

    # Find the blank cells in each of the required columns
    # and adds an error to the Audit_Result column.
    for column_name in required:
        df.loc[pd.isna(df[column_name]), 'Audit_Result'] = 'Missing required data'

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

    # Checks for dates to review for deletion that are expired or need manual review.
    inventory_df = check_dates(inventory_df)

    # Checks for mismatches between the inventory and Hub shares.
    inventory_df = check_inventory(inventory_df, shares)

    # Saves the inventory to a CSV for additional manual review.
    inventory_df['Audit_Result'] = inventory_df['Audit_Result'].replace('', 'Correct')
    csv_path = os.path.join(os.path.dirname(inventory_path),
                            f"digital_production_hub_audit_{datetime.date.today().strftime('%Y-%m')}.csv")
    inventory_df.to_csv(csv_path, index=False)
