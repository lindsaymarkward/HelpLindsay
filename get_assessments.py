"""Get CPXXXX assessment items from StudyFinder websites."""

import requests
import openpyxl

YEAR = 2020
START_STRING = "<h3>Subject Assessment</h3>"
OUTPUT_HTML_FILENAME = "output/assessments.html"
OUTPUT_EXCEL_FILENAME = "output/2021-IT-Assessment-Mapping.xlsx"
HTML_TOP = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>IT@JCU Assessments in CSDB/Studyfinder</title>
    <style type="text/css">
        table, td {
            border: thin black solid;
            padding: 0.5em;
            border-collapse: collapse;
            vertical-align: top;
        }
    </style>
</head>
<body>
<h1>IT@JCU Assessments in CSDB/Studyfinder</h1>
"""
HTML_BOTTOM = """
</body>
</html>
"""
WILL_WRITE_HTML = False


def main():
    subjects = ['CP1401', 'CP1402']
    # subjects = get_subjects()
    print(subjects)

    if WILL_WRITE_HTML:
        file_out = open(OUTPUT_HTML_FILENAME, 'w')
        print(HTML_TOP, file=file_out)
    subject_to_items = {}

    if WILL_WRITE_HTML:
        print(f"<table>", file=file_out)
    for subject in subjects:
        # Current year
        if WILL_WRITE_HTML:
            print(f"<tr>", file=file_out)
        for i in range(2):
            year_to_get = YEAR + i
            if WILL_WRITE_HTML:
                print(f"<td><h2>{subject} - {year_to_get}</h2>", file=file_out)
            url = f"https://secure.jcu.edu.au/app/studyfinder/index.cfm?subject={subject}&year={year_to_get}&transform=subjectwebview.xslt"
            response = requests.get(url)
            text = response.text
            assessment_block = get_assessment_block(text)
            print(assessment_block, file=file_out)
            items = extract_items(assessment_block)
            subject_to_items[subject] = items
            # print(subject_to_items)
            if WILL_WRITE_HTML:
                print(f"</td>", file=file_out)
        if WILL_WRITE_HTML:
            print(f"</tr>", file=file_out)
    if WILL_WRITE_HTML:
        print(f"</table>", file=file_out)

    if WILL_WRITE_HTML:
        print(HTML_BOTTOM, file=file_out)
        file_out.close()


def get_subjects():
    file_in = open("data/all_subjects.txt")
    subjects = [line.strip() for line in file_in]
    file_in.close()
    return subjects


def get_assessment_block(text):
    index_heading = text.find(START_STRING)
    index_end = text.find("</ul>", index_heading)
    section = text[index_heading + len(START_STRING):index_end + 6]
    section = section.replace('. ', '')
    return section.strip()


def extract_items(block):
    """Extract assessment items from HTML block as list of tuples."""
    items = []
    parts = block.split('\n')
    raw_items = [part.strip().strip('<li>').strip('</li>') for part in parts if part.strip().startswith('<li>')]
    for raw_item in raw_items:
        parts = raw_item.split(' - ')
        assessment = parts[0]
        weight = parts[1].strip('(').strip('%)')
        items.append((assessment, weight))
    return items


def write_spreadsheet():
    workbook = openpyxl.load_workbook(filename=OUTPUT_EXCEL_FILENAME)
    sheet = workbook['Assessment-Mapping']

    sheet.cell(row=12, column=1, value='Hello')
    workbook.save(filename=f"output/temp.xlsx")


# write_spreadsheet()

main()
