"""
Script for creating links for marking CP1406 A1 assignments - plan and site.
Requires student list CSV file with rows like, "Last name, First Name, jc123456\n"
tsv/cns: run twice; swap campusName/URL values
"""
__author__ = 'sci-lmw1'

# campusName = "Cairns"
# campusURL = "cns"
campusName = "Townsville"  # "External"
campusURL = "tsv"

filename = "CP1406{}Students.csv".format(campusName)
linkBase = "<a href=\"http://ditweb{}.jcu.edu.au/~".format(campusURL)
topSection = """<!doctype html>
<html>
<head>
  <title>CP1406, 2016-1 {0} - A1 Links</title>
  <meta charset="UTF-8">
    <style type="text/css">
        body {{ font-family: Arial, sans-serif; margin-left: 3em; }}
        h1, h2 {{ margin-left: -1em; }}
        h2 {{ margin-top: 1.5em; margin-bottom: 0.5em; }}
    </style>
</head>

<body>
    <h1>CP1406, 2016-1 {0} - Assignment 1 Links</h1>
    <ol>\n\n""".format(campusName)
bottomSection = """</ol>
</body>
</html>\n"""

inFile = open(filename, 'r')
outFile = open("CP1406{}A1links.html".format(campusName), 'w')
outFile.write(topSection)

for line in inFile:
    lastName, firstName, login = line.split(",")
    login = login.strip()

    linkLine = "<li>{0}{1}/a1/plan.html\" target=\"_blank\">{2} {3} ({1}) Plan</a> - {0}{1}/a1\" target=\"_blank\">Site</a></li>\n".format(
        linkBase, login, firstName, lastName)
    outFile.write(linkLine)
    # print(linkLine)

outFile.write(bottomSection)
inFile.close()
outFile.close()
