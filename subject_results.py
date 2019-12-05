"""
Create subject results comprehensive spreadsheet from:
- Class list from Student Management System (SMS)
- LearnJCU Ultra grade centre download/export
"""
import csv
import xlrd

DIRECTORY_DATA = 'data/subject_results'
FILE_CLASS_LIST = 'class_list_from_sms.csv'
FILE_GRADES = 'learnjcu_grade_centre.xls'
FILE_OUTPUT = 'blank_results.xlsx'


def main():
    """Create subject results comprehensive spreadsheet."""
    print("Welcome")
    students = get_students()
    print(f"Got {len(students)} students from {FILE_CLASS_LIST}")
    # print(students)


def get_students():
    """Get students as a list of tuples from the class list."""
    students = []  # list of tuples
    input_file = open(f"{DIRECTORY_DATA}/{FILE_CLASS_LIST}", 'r')
    input_file.readline()  # Ignore first header line
    fields = input_file.readline().split(',')  # Get field names
    index_id = fields.index('Student Id')
    index_name = fields.index('Student Name')
    # print(index_id, index_name)
    reader = csv.reader(input_file)
    for row in reader:
        student = row[index_id], row[index_name]
        students.append(student)
    input_file.close()
    return students


main()
