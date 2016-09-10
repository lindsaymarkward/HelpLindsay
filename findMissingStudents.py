"""
Compare two files of student emails (could be anything though)
Output all of the students who are in the first but not the second
"""
__author__ = 'Lindsay Ward'

# all_students = []
# existing_students = []

with open("data/allstudents.csv") as all_file:
    all_students = [line.strip() for line in all_file]
    all_students.sort()
# print(len(all_students), all_students)

with open("data/slackin.csv") as existing_file:
    existing_students = [line.strip() for line in existing_file]
    existing_students.sort()
# print(len(existing_students), existing_students)

new_students = [student for student in all_students if student not in existing_students]
# print(len(new_students), new_students)
print(len(new_students), "missing")
print("\n".join(new_students))
