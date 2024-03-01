"""
Experiment into automating the majority of the analysis for the Digital Production Hub audit
"""
import pandas as pd
import sys


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
    inventory_path = sys.argv[1]

    # Reads the inventory, a multiple sheet Excel spreadsheet, into one pandas dataframe, with cleanup.
    inventory_df = read_inventory(inventory_path)
