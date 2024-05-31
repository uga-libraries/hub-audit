# Hub Audit

## Overview

Automates the initial phase of the quarterly Hub Audit, which compares the Digital Production Hub share contents 
to the inventory and identifies information that needs to be updated.

## Getting Started

### Dependencies

TBD

### Installation

Download the "Digital Production Hub Inventory.xlsx" from the DCWG Teams Digital Production Hub folder.

Make a CSV with information about every share included in the audit, with the following columns:
- name
- path
- pattern
- folders

Name must match how the share is named within the Digital Production Hub Inventory.

Pattern is how the inventory is constructed. Current patterns:
- second: include the second level of folders, formatted top\second, for any top folder in the folders column
- share: the folder name in the inventory is the same as the share
- top: only include the top level of folders and files

Folders will only have a value if pattern is second. 
It is a pipe-separated list of folders where the second level of folders should also be included.

### Script Arguments

inventory (required): path to the Digital Production Hub Inventory.xlsx file

shares (required): path to the CSV with share information (see installation)

### Testing

There are unit tests for each function and for the entire script.
The input (inventories, share csvs, and share folders) is either in the repo or made by the test.

## Workflow

1. Download the Digital Production Hub Inventory spreadsheet and delete the "Hub Inventory Examples" tab.
   

2. Make the share CSV, if one does not already exist.
   
3. Run the script. 
   It will make a CSV in the same folder as the Hub Inventory spreadsheet which compares the shares to the inventory 
   and will print the number of lines in the inventory and size of the shares for the audit summary report.
   
4. Review the CSV created by the script and make any needed edits. 
   - Check for dates that need review (date to review is a time frame instead of a specific date) 
   - Check for inventory/share mismatches due to variations in how the folder was typed
   - Remove Thumbs.db and .DS_Store
   - Remove files in top level of directory structure related to Hub maintenance
   - Remove all files at the second level of directory structure (filter for "." in Folder)
   - Check for folders missing because the top and second level of folders was included in the inventory
   - Check for folders missing because the third level of folders was included in the inventory
   
5. Use the results to request changes from departments and to make the summary report.

## Author

Adriane Hanson, Head of Digital Stewardship, University of Georgia