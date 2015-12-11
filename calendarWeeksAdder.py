"""
Calendar (iCalendar format) file maker for JCU Study Periods
makes a .ics file that can be imported into Calendar programs
containing the weeks in a single study period,
including Lecture Recess (specified), O week, swotvac and exams
Uses icalendar package - https://pypi.python.org/pypi/icalendar
Lindsay Ward, JCU
11/12/2015
"""

from icalendar import Calendar, Event
from datetime import datetime, timedelta

__author__ = 'Lindsay Ward'
FILE_NAME = "JCU_Weeks.ics"
WEEKS_IN_STUDY_PERIOD = 13


def create_calendar():
    # get required dates - week 1 and lecture recess; others are derived
    week1text = input("Week 1 Date (dd/mm/yy): ")
    week1date = datetime.strptime(week1text, "%d/%m/%y").date()
    lecture_recess_text = input("Lecture Recess Date (dd/mm/yyyy): ")
    lecture_recess_date = datetime.strptime(lecture_recess_text, "%d/%m/%y").date()

    # create "calendar" to add events to
    cal = Calendar()

    # add O Week event (1 week before Week 1)
    event = Event()
    event.add('summary', 'O Week')
    event.add('dtstart', week1date - timedelta(days=7))
    cal.add_component(event)

    # loop through all numbered weeks
    week_date = week1date
    week_number = 1
    for i in range(WEEKS_IN_STUDY_PERIOD + 1):
        event = Event()
        # handle lecture recess, not incrementing week number
        if week_date == lecture_recess_date:
            event.add('summary', 'Lecture Recess')
        else:
            event.add('summary', 'Week ' + str(week_number))
            week_number += 1

        event.add('dtstart', week_date)
        cal.add_component(event)
        # add one week for next event
        week_date += timedelta(days=7)

    # add swotvac and exams after final week
    event = Event()
    event.add('summary', 'Swotvac')
    event.add('dtstart', week_date)
    week_date += timedelta(days=7)
    cal.add_component(event)

    event = Event()
    event.add('summary', 'Exams')
    event.add('dtstart', week_date)
    cal.add_component(event)

    # write calendar file to disk (open the file to add events to Calendar program)
    calendar_file = open(FILE_NAME, 'wb')
    calendar_file.write(cal.to_ical())
    calendar_file.close()

create_calendar()
