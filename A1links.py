"""
Script for creating links for marking CP1406 A1 assignments - plan and site.
Requires student list CSV file with rows in the form, "Last name, First Name, jc123456"
(note: external students should go in Townsville file)
"""
from collections import namedtuple
__author__ = 'Lindsay Ward'

INPUT_DIR = 'data'
OUTPUT_DIR = 'output'

Campus = namedtuple('Campus', ['name', 'URL'])
campuses = (Campus('Cairns', 'cns'), Campus('Townsville', 'tsv'))

# do the same thing for each campus
for campus in campuses:
    filename = "{}/CP1406{}Students.csv".format(INPUT_DIR, campus.name)
    linkBase = "<a href=\"http://ditweb{}.jcu.edu.au/~".format(campus.URL)
    topSection = """<!doctype html>
<html>
<head>
  <title>CP1406 {0} - A1 Links</title>
  <meta charset="UTF-8">
  <style type="text/css">
    body {{ font-family: Arial, sans-serif; margin-left: 3em; }}
    h1, h2 {{ margin-left: -1em; }}
    h2 {{ margin-top: 1.5em; margin-bottom: 0.5em; }}
  </style>
</head>

<body>
    <h1>CP1406 {0} - Assignment 1 Links</h1>
    <ol>\n""".format(campus.name)
    bottomSection = """</ol>\n</body>\n</html>\n"""

    inFile = open(filename, 'r')
    outFile = open("{}/CP1406{}A1links.html".format(OUTPUT_DIR, campus.name), 'w')
    outFile.write(topSection)

    for line in inFile:
        lastName, firstName, login = line.strip().split(",")
        linkLine = "<li>{0}{1}/a1/plan.html\" target=\"_blank\">{2} {3} ({1}) Plan</a> - {0}{1}/a1\" target=\"_blank\">Site</a></li>\n".format(
            linkBase, login, firstName, lastName)
        outFile.write(linkLine)
        # print(linkLine)

    outFile.write(bottomSection)
    inFile.close()
    outFile.close()
