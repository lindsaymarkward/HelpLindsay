"""Program for creating ACC Board folders and subfolders."""

import calendar
import os
from datetime import datetime

# START_PATH = '/Users/sci-lmw1/Downloads/temp'  # For testing
START_PATH = '/Users/sci-lmw1/Library/CloudStorage/OneDrive-AnnandaleChristianCollege/Board/Board Meetings/2024'

# Create folder names for the year
current_year = datetime.now().year
months = list(calendar.month_name)[1:]  # Skip the empty string at index 0
all_folders = [f"{i:02d} {month} {current_year}" for i, month in enumerate(months, 1)]

top_folders = all_folders[:]  # Select only the ones we haven't already made (customise as needed)
print(top_folders)
input()

for folder in top_folders:
    os.chdir(START_PATH)
    os.mkdir(folder)
    os.chdir(folder)
    os.mkdir('Correspondence')
    os.mkdir('Reports')
    os.chdir('Reports')
    os.mkdir('Principal')
    os.mkdir('BM')
