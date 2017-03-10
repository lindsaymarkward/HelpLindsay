"""
Compare two files of values (e.g. student emails)
Output all of the values that are in the first but not the second file
"""


with open("allstudents.csv") as all_file:
    new_values = set([line.strip() for line in all_file])

with open("data/slackin.csv") as existing_file:
    existing_values = set([line.strip() for line in existing_file])

missing_values = [student for student in new_values if student not in existing_values]
print(len(missing_values), "missing")
print("\n".join(missing_values))
