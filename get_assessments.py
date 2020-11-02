"""Get CPXXXX assessment items from StudyFinder websites."""

import requests

YEAR = 2020
START_STRING = "<h3>Subject Assessment</h3>"
OUTPUT_FILENAME = "output/assessments.html"
HTML_TOP = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>IT@JCU Assessments in CSDB/Studyfinder</title>
</head>
<body>
<h1>IT@JCU Assessments in CSDB/Studyfinder</h1>
"""
HTML_BOTTOM = """
</body>
</html>
"""


def main():
    subjects = ['CP1401', 'CP1402']
    # file_in = open("data/all_subjects.txt")
    # subjects = [line.strip() for line in file_in]
    # file_in.close()
    print(subjects)

    file_out = open(OUTPUT_FILENAME, 'w')
    print(HTML_TOP, file=file_out)

    for subject in subjects:
        url = f"https://secure.jcu.edu.au/app/studyfinder/index.cfm?subject={subject}&year={YEAR}&transform=subjectwebview.xslt"
        response = requests.get(url)
        text = response.text
        assessment_block = get_assessment_block(text)
        print(f"<h2>{subject}</h2>", file=file_out)
        print(assessment_block, file=file_out)

    print(HTML_BOTTOM, file=file_out)
    file_out.close()


def get_assessment_block(text):
    index_heading = text.find(START_STRING)
    index_end = text.find("</ul>", index_heading)
    section = text[index_heading + len(START_STRING):index_end + 6]
    return section.strip()


main()

# block = """<h3>Subject Assessment</h3>
#
#    <ul>
#       <li>Practicals - (40%)</li>
#       <li>Assignment 1 - (30%)</li>
#       <li>Assignment 2 - (30%). </li>
#    </ul>"""
# print(repr(get_assessment_block(block)))
# print(block)
# parts = block.split('\n')
# items = [part.strip().strip('<li>').strip('</li>') for part in parts if part.strip().startswith('<li>')]
# print(items)
