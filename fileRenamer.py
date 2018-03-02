"""
File renaming script - for renaming files downloaded from LearnJCU, like:
E.g. Assignment 1 - Two CMS Startup_jc123456_attempt_2016-03-29-22-53-56_a1
Lindsay Ward, 12/09/2011
Modified 16/06/2014 - just use .replace instead of slicing the start
"""

import os

# Remove start (from LearnJCU)
LENGTH_OF_TEXT_TO_REMOVE = 28
START_TEXT = "Assessment Item 4_"
DIRECTORY = "/Users/sci-lmw1/Downloads/DT"

os.chdir(DIRECTORY)
for filename in os.listdir('.'):
    # print(filename)
    if filename.endswith('.txt'):
        os.remove(filename)
    elif filename.startswith(START_TEXT):
        # Remove LearnJCU's massive file name text and also the "attempt" text
        newName = filename.replace(START_TEXT, "")
        # Find start of "attempt" and remove it and date/time that follows
        # (LENGTH_OF_TEXT_TO_REMOVE characters)
        start = newName.find("attempt")
        newName = newName.replace(
            newName[start:start + LENGTH_OF_TEXT_TO_REMOVE], "")
        os.rename(filename, newName)
        # print(newName)

"""
# Replace %20 with space
os.chdir("/Users/sci-lmw1/Google Drive/JCU General/Resource Packages (Templates)/")
for filename in os.listdir('.'):
    newName = filename.replace("%20", " ")
    os.rename(filename, newName)
"""
