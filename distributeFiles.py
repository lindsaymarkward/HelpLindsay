"""
Move files that start with number XX to folders that end with XX
(Lecture notes folder to weekly folders)
"""
import os, shutil
__author__ = 'Lindsay Ward'

NOTES_PATH = '/Users/sci-lmw1/GoogleDrive/OffCampus/JCUS/CP1406/CP1406 2016 SP51/_Lecture Notes'

os.chdir(NOTES_PATH)

for filename in os.listdir('.'):
    prefix = filename[:2]

    if prefix.isdigit():
        # print(prefix)
        shutil.move(filename, '../Week ' + prefix + '/' + filename)
        # print('../Week ' + prefix + '/' + filename)
