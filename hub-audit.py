"""
Experiment into automating the majority of the analysis for the Digital Production Hub audit
"""
import pandas as pd
import sys


def read_inventory(path):
    """Read inventory into dataframe, drop unneeded rows, and add a column"""
    # Reads every sheet in the Excel spreadsheet into a single dataframe.
    df = pd.concat(pd.read_excel(path, sheet_name=None), ignore_index=True)

    # Removes the rows that describe each column.
    df = df[df['Share (required)'] != 'Name of the Hub share.']

    # Removes the rows of content that has been deleted (deleted date column is not blank).
    df = df[df['Deleted (date) (optional)'].isnull()]

    # Removes blank rows.
    df = df.dropna(how='all')

    # Adds a new column for recording errors.
    df['Audit_Result'] = ''

    return df


if __name__ == '__main__':

    # Path to the inventory (from the script argument).
    inventory_path = sys.argv[1]

    # Reads every sheet of the inventory, which is an Excel spreadsheet, into a pandas dataframe.
    inventory_df = read_inventory(inventory_path)
