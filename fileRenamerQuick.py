"""
Rename files in a directory by replacing text
"""
import os

FROM_TEXT = "Workshop"
TO_TEXT = "Practical"
DIRECTORY = "/Users/sci-lmw1/GoogleDrive/CP1404/CP1404 2016-2/workshop originals"

os.chdir(DIRECTORY)
for filename in os.listdir('.'):
    print(filename)
    if FROM_TEXT in filename:
        newName = filename.replace(FROM_TEXT, TO_TEXT)
        os.rename(filename, newName)
        # print(newName)
