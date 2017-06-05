"""
File renaming script - for renaming files downloaded from LearnJCU, like:
    Assignment 1 - Two CMS Startup_jc209333_attempt_2016-03-29-22-53-56_a1
Lindsay Ward, 12/09/2011
Modified 16/06/2014 - just use .replace instead of slicing the start; assume that's safe
"""

import os

# Remove start (from LearnJCU)
LENGTH_OF_TEXT_TO_REMOVE = 28
START_TEXT = "Assessment Task 1 - Initial Project Plan_"
DIRECTORY = "/Users/sci-lmw1/Downloads/DT_A1"

os.chdir(DIRECTORY)
for filename in os.listdir('.'):
    print(filename)
    # if filename == ".DS_Store":
    #     os.remove(filename)
    # continue
    if filename.startswith(START_TEXT):
        # get rid of LearnJCU's massive file name text and also the "attempt" text
        newName = filename.replace(START_TEXT, "")
        # find start of "attempt" and remove it and date/time that follows (LENGTH_OF_TEXT_TO_REMOVE characters)
        start = newName.find("attempt")
        newName = newName.replace(
            newName[start:start + LENGTH_OF_TEXT_TO_REMOVE], "")
        # when testing, I use the print line and comment out the rename line, then I swap them over
        os.rename(filename, newName)
        # print(newName)

"""
# Replace %20 with space
os.chdir("/Users/sci-lmw1/Google Drive/JCU General/Resource Packages (Templates)/")
for filename in os.listdir('.'):
    newName = filename.replace("%20", " ")
    os.rename(filename, newName)
"""
