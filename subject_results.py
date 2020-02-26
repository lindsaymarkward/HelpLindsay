"""
Create subject results comprehensive spreadsheet from:
- Class list from Student Management System (SMS)
- LearnJCU Ultra grade centre download/export
- Blank subject results spreadsheet (template)

TODO: Add error-checking for grade centre sheet (<= 5 assessment items)
"""
import csv
import openpyxl

# Constants ordered/grouped by relevant spreadsheet
DIRECTORY_DATA = 'data/subject_results'
FILE_RESULTS = 'blank_results.xlsx'

FILE_CLASS_LIST = 'class_list_from_sms.csv'
COLUMN_CLASS_LIST_ID = 13  # N

FILE_GRADE_CENTRE = 'learnjcu_grade_centre.xls'
LAST_HEADING_BEFORE_ASSESSMENTS = 'Child Subject ID'
SHEET_STUDENT = 'StudentOne'
SHEET_RESULTS = 'RawResults'
ROW_FIRST_STUDENT_ONE = 3
ROW_FIRST_RAW_DATA = 13
COLUMN_GRADE_CENTRE_ID = 3
COLUMN_GRADE_CENTRE_FIRST_ASSESSMENT = 5


def main():
    """Create subject results comprehensive spreadsheet."""
    print("Welcome")
    students_class_list = get_students()
    print(f"Got {len(students_class_list)} students from {FILE_CLASS_LIST}")

    # add_students_to_results(students_class_list)
    assessments, student_grade_centre_rows = get_assessments()
    # assessments = [(7, 'Assignment 1 - Movies to Watch 1.0', 100.0), (8, 'Assignment 2 - Movies to Watch 2.0', 100.0), (9, 'Pracs', 30.0)]
    student_results = get_student_results(student_grade_centre_rows, students_class_list, assessments)
    if len(students_class_list) != len(student_results):
        print("ERROR: Student results don't match class list")
    write_results(student_results, students_class_list, assessments)


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


def get_assessments():
    """Extract assessment details from LearnJCU Grade Centre sheet."""
    # File from LearnJCU is UTF-16 encoded tab-delimited CSV with XLS extension
    input_file = open(f"{DIRECTORY_DATA}/{FILE_GRADE_CENTRE}", 'r', encoding='utf-16')
    rows = list(csv.reader(input_file, delimiter="\t"))
    input_file.close()
    headings = rows[0]

    # Assessments start after the column with heading LAST_HEADER_BEFORE_ASSESSMENTS
    first_assessment_index = headings.index(LAST_HEADING_BEFORE_ASSESSMENTS) + 1
    assessment_headings = headings[first_assessment_index:]
    assessments = []
    # Assessment names look like:
    # heading = "Assignment 1 - Movies to Watch 1.0 [Total Pts: 100 Score] |660463"
    # heading = "Pracs [Total Pts: up to 30 Score] |789219"
    for i, heading in enumerate(assessment_headings):
        heading = heading.replace("up to ", "")  # for total columns
        parts = heading.split(" [Total Pts: ")
        title = parts[0]
        score = float(parts[1].split()[0])
        assessments.append((first_assessment_index + i, title, score))
    # Return both processed assessments and rest of student data rows
    return assessments, rows[1:]


def get_student_results(student_grade_centre_rows, students, assessments):
    student_results = []
    grade_centre_ids = [row[COLUMN_GRADE_CENTRE_ID] for row in student_grade_centre_rows]
    for student in students:
        student_id = student[COLUMN_CLASS_LIST_ID]
        student_name = student[COLUMN_CLASS_LIST_ID + 1]
        student_result = [student_id, student_name]
        try:
            index = grade_centre_ids.index(student_id)
            # print(f"{student_name} is at row {index}")
        except ValueError:
            print(f"ERROR: Student: {student_name} ({student_id}) not in the LearnJCU Grade Centre sheet")
            continue
        for assessment in assessments:
            # Replace non-scores like 'In Progress' or 'Needs Grading' with blanks
            try:
                score = float(student_grade_centre_rows[index][assessment[0]])
            except ValueError:
                score = None
            student_result.append(score)
        student_results.append(student_result)
    return student_results


def write_results(student_results, class_list, assessments):
    """Write student details and scores to results spreadsheet."""
    workbook = openpyxl.load_workbook(filename=f"{DIRECTORY_DATA}/{FILE_RESULTS}")
    # Add student scores to results data sheet
    sheet = workbook[SHEET_STUDENT]
    # Write all data from class list to results StudentOne sheet
    for i, student in enumerate(class_list):
        current_row = ROW_FIRST_STUDENT_ONE + i
        for j, value in enumerate(student, 1):
            sheet.cell(row=current_row, column=j, value=value)
        # Write reference to grade
        reference_row = ROW_FIRST_RAW_DATA + i
        sheet.cell(row=current_row, column=16, value=f"={SHEET_RESULTS}!M{reference_row}")

    # Add formulas to raw results sheet (just student ID and name)
    sheet = workbook[SHEET_RESULTS]
    for i in range(len(class_list)):
        current_row = ROW_FIRST_RAW_DATA + i
        reference_row = ROW_FIRST_STUDENT_ONE + i
        sheet.cell(row=current_row, column=2, value=f"={SHEET_STUDENT}!N{reference_row}")
        sheet.cell(row=current_row, column=3, value=f"={SHEET_STUDENT}!O{reference_row}")

    # Add assessment headings (E10-J12, 10=%, 11=Out Of, 12=Description)
    # assessment looks like (7, 'Assignment 1 - Movies to Watch 1.0', 100.0)
    for i, assessment in enumerate(assessments):
        # Unsure if possible to get %. Could get staff to enter it in Grade Centre
        sheet.cell(row=11, column=COLUMN_GRADE_CENTRE_FIRST_ASSESSMENT + i, value=assessment[2])
        sheet.cell(row=12, column=COLUMN_GRADE_CENTRE_FIRST_ASSESSMENT + i, value=assessment[1])

    # Add scores
    for i, current_student_results in enumerate(student_results):
        current_row = ROW_FIRST_RAW_DATA + i
        for j, score in enumerate(current_student_results[2:]):
            if score is None:  # Don't write blanks
                continue
            current_column = COLUMN_GRADE_CENTRE_FIRST_ASSESSMENT + j
            sheet.cell(row=current_row, column=current_column, value=score)
    workbook.save(filename='test_output.xlsx')  # TODO: temporary. Save actual file.


main()
