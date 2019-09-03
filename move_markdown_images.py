"""
Move ./prac_01/media/image1.png etc. to ./images/prac_01_image1.png
and update links in ./prac_01/README.md to match
"""

import shutil
import os

# DIRECTORY = "/Users/sci-lmw1/OneDrive - James Cook University/Subjects/CP1404/_Master Documents/Practical Markdown"
DIRECTORY = "/Users/sci-lmw1/dev/CP1404/Practicals"
SUBSTITUTIONS = {'\_': '_', '\\"': '"', "\\'": "'", "\*": "*", '**"': '"', '"**': '"', "**'": "'", "'**": "'",
                 "{.underline}": "", "\#": "#", '\$': '$'}
os.chdir(DIRECTORY)
root_directory = os.getcwd()

for directory_name, subdirectories, filenames in os.walk('.'):
    # print("Directory:", directory_name)
    # print("\tcontains subdirectories:", subdirectories)
    # print("\tand files:", filenames)

    if '.git' in directory_name or '.idea' in directory_name:
        continue
    try:
        start = directory_name.index('_') + 1
        prac_number_text = directory_name[start:start + 2]
    except ValueError as error:
        # print(directory_name, error)
        continue

    # process README in the prac folders
    if directory_name[:-2].endswith('prac_'):
        prac_filename = "{}/README.md".format(os.path.join(directory_name))
        try:
            with open(prac_filename) as in_file:
                print('opening', prac_filename)
                text = in_file.read()

                for old, new in SUBSTITUTIONS.items():
                    text = text.replace(old, new)

                # text = text.replace('\\\n', '  \n')
                # text = text.replace('./media/image', '../images/{}image'.format(prac_number_text))
                # text = text.replace('\...', '...')

                # remove image sizes
                # while '.png){' in text:
                #     start = text.index('.png){') + 5
                #     end = text.index('"}') + 2
                #     print("Replacing {} to {}".format(start, end))
                #     text = text.replace(text[start:end], "")

            with open(prac_filename, 'w') as out_file:
                out_file.write(text)
                # pass

        except FileNotFoundError as error:
            print(error)
            continue

    # move image files
    elif directory_name.endswith('media'):
        continue  # temp (done!)
        try:
            print(directory_name, "has", filenames)
            for filename in filenames:
                # create new filename based on the prac number (always fixed size)
                new_filename = prac_number_text + filename
                old_full_path = os.path.join(directory_name, filename)
                new_full_path = os.path.join('./images', new_filename)
                print("moving {} to {}".format(old_full_path, new_full_path))
                # shutil.move(old_full_path, new_full_path)
                os.rename(old_full_path, new_full_path)
            pass
        except:
            # if folder contains no images/media, move along
            continue

    # remove unwanted files
    # for filename in filenames:
    #     # print(filename)
    #     if filename in ['.DS_Store', "Icon\r"]:
    #         os.remove(filename)
