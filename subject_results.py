"""
Create subject results comprehensive spreadsheet from:
- Class list from Student Management System (SMS)
- LearnJCU Ultra grade centre download/export
- Blank subject results spreadsheet (template)

How To:
Update user-customisable constants for desired directory
Download LearnJCU Grade Centre file (xls extension but actually a CSV) to DIRECTORY_DATA folder
Edit grade centre spreadsheet so that:
- only desired assessments are present, in desired order
- replace number/id after pipe | with assessment weighting (e.g. Assignment 1 [Total Pts: 100 Score] |20)
Put all related student class list CSV files in DIRECTORY_DATA
Run
Output files will go into 'output' folder,
Names will match class list CSV file names + "Results" - csv & xlsx
Edit these to confirm all is OK
NO Guarantees are given with this program :)

TODO: Add error-checking for grade centre sheet (<= 5 assessment items)
"""
import csv
import openpyxl
import os
import warnings
import xlwings

# User-defined constants
DIRECTORY_DATA = 'data/subject_results'
DIRECTORY_OUTPUT_NAME = 'output'
FILE_RESULTS_BLANK = 'CP-2020-1-Results.xlsx'
FILE_GRADE_CENTRE = 'learnjcu_grade_centre.xls'
FILE_IN_CLASS_LIST = 'CP3402 Townsville SP1 2020.csv'

# Internal constants that might change if spreadsheet structure changes
SHEET_STUDENT = 'StudentOne'
SHEET_RESULTS = 'RawResults'
COLUMN_CLASS_LIST_ID = 13  # N
LAST_HEADING_BEFORE_ASSESSMENTS = 'Child Subject ID'  # for the column number without using an absolute number
ROW_FIRST_STUDENT_ONE = 3
ROW_FIRST_RAW_DATA = 13
COLUMN_GRADE_CENTRE_ID = 3  # Numbered from 1 (csv)
COLUMN_RESULTS_FIRST_ASSESSMENT = 5  # Numbered from 0 (openpyxl)
COLUMN_RESULTS_FINAL_GRADE = 'O'  # O for U/S/X grades in 2020-1


def main():
    """Create subject results comprehensive spreadsheet."""
    warnings.filterwarnings("ignore")

    # create output folder
    try:
        os.mkdir(f"{DIRECTORY_DATA}/{DIRECTORY_OUTPUT_NAME}")
    except FileExistsError:
        pass
    # create filenames
    input_filename_base = FILE_IN_CLASS_LIST.split('.')[0]  # no extension
    output_filename_base = input_filename_base + "-Results"

    students_class_list = get_students()
    print(f"Got {len(students_class_list)} students from {FILE_IN_CLASS_LIST}")

    # add_students_to_results(students_class_list)
    assessments, student_grade_centre_rows = get_assessments()
    print(f"Got {len(assessments)} assessments from {FILE_GRADE_CENTRE}")

    # assessments = [(7, 'Assignment 1', 100.0, 10), (8, 'Assignment 2', 100.0, 20)]
    student_results = get_student_results(student_grade_centre_rows, students_class_list, assessments)
    if len(students_class_list) != len(student_results):
        print("ERROR: Student results don't match class list")
        return  # TODO: raise exception
    print(f"Got {len(student_results)} students' results from {FILE_GRADE_CENTRE}")
    write_results(student_results, students_class_list, assessments, output_filename_base + ".xlsx")
    write_csv(output_filename_base)
    print(f"Results spreadsheets created: {DIRECTORY_DATA}/{DIRECTORY_OUTPUT_NAME}/{output_filename_base} .xlsx & .csv")


def get_students():
    """Get students as a list of tuples from the class list."""
    students = []  # list of rows/lists
    input_file = open(f"{DIRECTORY_DATA}/{FILE_IN_CLASS_LIST}", 'r')
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
    # Assessment data looks like (last value set manually in spreadsheet):
    # heading = "Assignment 1 - Movies to Watch 1.0 [Total Pts: 100 Score] |20"
    # heading = "Pracs [Total Pts: up to 30 Score] |10"
    for i, heading in enumerate(assessment_headings):
        try:
            heading = heading.replace("up to ", "")  # for total columns
            parts = heading.split(" [Total Pts: ")
            title = parts[0]
            sub_parts = parts[1].split()
            score = float(sub_parts[0])
            weight = int(sub_parts[-1].strip('|'))
            assessments.append((first_assessment_index + i, title, score, weight))
        except IndexError:
            print(f"ERROR with format of {DIRECTORY_DATA}/{FILE_GRADE_CENTRE}")
            return None  # TODO raise exception
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
            # Handle things like "Reply to Post(81.60)" in LearnJCU with total column
            # Replace non-scores like 'In Progress' or 'Needs Grading' with blanks
            try:
                score = float(student_grade_centre_rows[index][assessment[0]])
            except ValueError:
                score = None
            student_result.append(score)
        student_results.append(student_result)
    return student_results


def write_results(student_results, class_list, assessments, output_filename):
    """Write student details and scores to results spreadsheet."""
    workbook = openpyxl.load_workbook(filename=f"{DIRECTORY_DATA}/{FILE_RESULTS_BLANK}")
    # Add student scores to results data sheet
    sheet = workbook[SHEET_STUDENT]
    # Write all data from class list to results StudentOne sheet
    for i, student in enumerate(class_list):
        current_row = ROW_FIRST_STUDENT_ONE + i
        for j, value in enumerate(student, 1):
            sheet.cell(row=current_row, column=j, value=value)
        # Write reference to grade
        reference_row = ROW_FIRST_RAW_DATA + i
        sheet.cell(row=current_row, column=16, value=f"={SHEET_RESULTS}!{COLUMN_RESULTS_FINAL_GRADE}{reference_row}")

    # Add formulas to raw results sheet (just student ID and name)
    sheet = workbook[SHEET_RESULTS]
    for i in range(len(class_list)):
        current_row = ROW_FIRST_RAW_DATA + i
        reference_row = ROW_FIRST_STUDENT_ONE + i
        sheet.cell(row=current_row, column=2, value=f"={SHEET_STUDENT}!N{reference_row}")
        sheet.cell(row=current_row, column=3, value=f"={SHEET_STUDENT}!O{reference_row}")

    # Add assessment headings (E10-J12, 10=%, 11=Out Of, 12=Description)
    # assessment looks like (7, 'Assignment 1 - Movies to Watch 1.0', 100.0, 20)
    for i, assessment in enumerate(assessments):
        # Note: staff need to enter weight in Grade Centre
        weight_to_write = assessment[3] / 100  # Need 0-1 instead of 0-100 for % in spreadsheet
        sheet.cell(row=10, column=COLUMN_RESULTS_FIRST_ASSESSMENT + i, value=weight_to_write)
        sheet.cell(row=11, column=COLUMN_RESULTS_FIRST_ASSESSMENT + i, value=assessment[2])
        sheet.cell(row=12, column=COLUMN_RESULTS_FIRST_ASSESSMENT + i, value=assessment[1])

    # Add scores
    for i, current_student_results in enumerate(student_results):
        current_row = ROW_FIRST_RAW_DATA + i
        for j, score in enumerate(current_student_results[2:]):
            if score is None:  # Don't write blanks
                continue
            current_column = COLUMN_RESULTS_FIRST_ASSESSMENT + j
            sheet.cell(row=current_row, column=current_column, value=score)
    workbook.save(filename=f"{DIRECTORY_DATA}/{DIRECTORY_OUTPUT_NAME}/{output_filename}")


def write_csv(filename_base):
    """Write just CSV file needed for results submission."""
    input_filename = filename_base + ".xlsx"
    output_filename = filename_base + ".csv"
    # openpyxl does not evaluate formulas, so use xlwings
    excel_app = xlwings.App(visible=False)
    excel_book = excel_app.books.open(f"{DIRECTORY_DATA}/{DIRECTORY_OUTPUT_NAME}/{input_filename}")
    sheet = excel_book.sheets[SHEET_STUDENT]
    with open(f"{DIRECTORY_DATA}/{DIRECTORY_OUTPUT_NAME}/{output_filename}", 'w', newline="") as f:
        writer = csv.writer(f)
        for row in sheet.range('A1').current_region.value:
            writer.writerow(row)
    excel_book.save()
    excel_book.close()
    excel_app.quit()


main()
