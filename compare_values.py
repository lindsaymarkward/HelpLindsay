"""
Compare two files of values (e.g. student emails)
Output all of the values that are in the first but not the second file
"""


# with open("first.txt") as all_file:
#     new_values = set([line.strip() for line in all_file])
#
# with open("second.txt") as existing_file:
#     existing_values = set([line.strip() for line in existing_file])

with open("output/nonslackers.txt") as all_file:
    new_values = set([line.strip() for line in all_file.read().split(',')])

with open("output/nonslackers_170310_invited.txt") as existing_file:
    existing_values = set([line.strip() for line in existing_file.read().split(',')])

missing_values = [student for student in new_values if student not in existing_values]
print(len(missing_values), "missing")
print("\n".join(missing_values))
