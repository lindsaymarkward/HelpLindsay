"""
Move ./prac_01/media/image1.png etc. to ./images/prac_01_image1.png
and update links in ./prac_01/README.md to match
"""

import os


DIRECTORY = "/Users/sci-lmw1/GoogleDrive/CP1404/_Master Documents/Practical Markdown"

os.chdir(DIRECTORY)
root_directory = os.getcwd()

for directory_name, subdirectories, filenames in os.walk('.'):
    # print("Directory:", directory_name)
    # print("\tcontains subdirectories:", subdirectories)
    # print("\tand files:", filenames)

    if not directory_name[:-2].endswith('prac_'):
        continue
    os.chdir(directory_name)
    print("(Current working directory is: {})".format(os.getcwd()))

    try:
        with open('README.md') as in_file:
            text = in_file.read()
            text = text.replace('./media/image1.png', '../images/image1.png')

        with open('README.md', 'w') as out_file:
            out_file.write(text)

    except FileNotFoundError:
        continue

    for filename in filenames:
        # print(filename)
        if filename in ['.DS_Store', "Icon\r"]:
            os.remove(filename)
    os.chdir(root_directory)
