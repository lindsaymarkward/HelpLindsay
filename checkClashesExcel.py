"""
Read an Excel file containing multiple subject lists, as exported by StaffOnline
and report all students doing combinations of subjects & number who have those
"""
import openpyxl

SHEET_NAME = "Sheet1"

__author__ = 'sci-lmw1'
FILENAME = '3rdYear.xlsx'
# FILENAME = 'Classlists.xlsx'
CAMPUSES = ["CNS", "TSV"]


def main():
    students, subjects = get_students_subjects()

    combinations = make_combinations(subjects)
    # print(combinations)
    print_clashes(combinations, students)
    # print_class_lists(students, subjects)


def print_clashes(combinations, students):
    """
    Print all students who have clashes with any combination of subjects, by campus
    :param combinations: list of combinations of multiple subjects
    :param students: dictionary of student data containing what subjects they take
    """
    for combo in combinations:
        print(combo)
        for campus in CAMPUSES:
            print(campus, end=": ")
            count = 0
            for student in students[campus]:
                if set(students[campus][student]) == combo:
                    print(student, end=', ')
                    count += 1
            print("", count)


def print_class_lists(students, subjects):
    """
    print class lists by campus
    :param students: dictionary of student data
    :param subjects: list of all subjects
    :return:
    """
    for subject in subjects:
        print(subject)
        for campus in CAMPUSES:
            print(campus, end=": ")
            for student in students[campus]:
                if subject in students[campus][student]:
                    print(student, end=' ')
            print()


def get_students_subjects():
    """
    Read Excel class list file and generate dictionary of students and list of subjects
    :return: students (dictionary containing subjects they do) and subjects (list)
    """
    class_workbook = openpyxl.load_workbook(FILENAME)
    class_sheet = class_workbook.get_sheet_by_name(SHEET_NAME)
    # map student names to list of subjects in a dictionary with items for each campus
    students = {"CNS": {}, "TSV": {}}
    subjects = []
    # first row is header, last row is total
    for i in range(1, class_sheet.max_row - 1):
        # convert cells to text in those cells (.value)
        cell_text = [cell.value for cell in class_sheet.rows[i]]
        # print(cell_text)
        if cell_text[2] is None:
            cell_text[2] = ""
        name = "{} {}".format(cell_text[2], cell_text[1])
        subject = cell_text[11]
        campus = cell_text[12]
        # print(name, subject, campus)

        # build list of unique subjects
        if subject not in subjects:
            subjects.append(subject)

        # add student to dictionary
        if name not in students[campus]:
            students[campus][name] = [subject]
        else:
            students[campus][name].append(subject)

    return students, subjects


def make_combinations(values):
    """
    Get all combinations of _multiple_ values within a set of values
    technique based on https://en.wikipedia.org/wiki/Combination#Enumerating_k-combinations
    :param values: a list of values
    :return: list of all combinations
    """
    combinations = {frozenset(values)}
    print(combinations)
    n = len(values)
    # loop through all relevant bit strings (non-zero, non-all-1's)
    for i in range(1, 2 ** n - 1):
        # print(bin(i))
        # print(str(bin(i)))
        bit_string = "{:0{}b}".format(i, n)
        if bit_string.count('1') > 1:
            # print(bit_string)
            combo = set()
            for i, char in enumerate(bit_string):
                if char == '1':
                    combo.add(values[i])
            combinations.add(frozenset(combo))
    return combinations
    # print(len(combinations), combinations)

main()
