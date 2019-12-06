"""
Create subject results comprehensive spreadsheet from:
- Class list from Student Management System (SMS)
- LearnJCU Ultra grade centre download/export
"""
import csv
import openpyxl

DIRECTORY_DATA = 'data/subject_results'
FILE_CLASS_LIST = 'class_list_from_sms.csv'
FILE_GRADE_CENTRE = 'learnjcu_grade_centre.xls'
FILE_RESULTS = 'blank_results.xlsx'


def main():
    """Create subject results comprehensive spreadsheet."""
    print("Welcome")
    students = get_students()
    print(f"Got {len(students)} students from {FILE_CLASS_LIST}")
    # print(students)

    add_students_to_results(students)


def get_students():
    """Get students as a list of tuples from the class list."""
    students = []  # list of rows/lists
    input_file = open(f"{DIRECTORY_DATA}/{FILE_CLASS_LIST}", 'r')
    input_file.readline()  # Ignore first header line
    input_file.readline()  # Ignore second header line
    reader = csv.reader(input_file)
    for row in reader:
        student = row
        students.append(student)
    input_file.close()
    return students


def add_students_to_results(students):
    """Add students to StudentOne data sheet."""
    workbook = openpyxl.load_workbook(filename=f"{DIRECTORY_DATA}/{FILE_RESULTS}")
    sheet = workbook['StudentOne']
    first_row = 3
    for i, student in enumerate(students):
        for j, value in enumerate(student, 1):
            sheet.cell(row=first_row + i, column=j, value=value)
    workbook.save(filename='test_output.xlsx')


main()
