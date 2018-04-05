"""Prompt and rename audio files after playing them with VLC."""
# This script is an answer to:
# https://stackoverflow.com/questions/49643892/batch-file-to-give-the-rename-prompt-in-windows/

import os
import subprocess

COMMAND = "/Applications/VLC.app/Contents/MacOS/VLC"
ARGUMENTS = "--play-and-exit"
DIRECTORY = "/Users/sci-lmw1/dev/temp/"

os.chdir(DIRECTORY)
for filename in os.listdir('.'):
    # ignore directories, just process files
    if not os.path.isdir(filename):
        subprocess.call([COMMAND, ARGUMENTS, filename])
        new_name = input("New name for {}: ".format(filename))
        os.rename(filename, new_name)
