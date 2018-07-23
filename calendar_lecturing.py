"""
Calendar (iCalendar format) file maker for JCU teaching
makes a .ics file that can be imported into calendar programs
including Lecture Recess (specified), O week, swotvac and exams
Uses icalendar package - https://pypi.python.org/pypi/icalendar
Lindsay Ward, JCU
29/06/2018
"""

from icalendar import Calendar, Event
from datetime import datetime, timedelta

__author__ = 'Lindsay Ward'
FILE_NAME = "output/my_teaching.ics"
WEEKS_IN_STUDY_PERIOD = 13
LECTURES = [("CP1404", )]  # date of first lecture
PRACTICALS = []


def create_on_campus_calendar():
    """
    Create a calendar file with teaching schedule based on hard-coded data
    """

    # create "calendar" to add events to
    cal = Calendar()

    study_periods = ["SP1", "SP2"]
    for study_period in study_periods:

        # get required dates - week 1 and lecture recess; others are derived
        week1text = input(study_period + " Week 1 Date (dd/mm/yy): ")
        week1date = datetime.strptime(week1text, "%d/%m/%y").date()
        lecture_recess_text = input("Lecture Recess Date (dd/mm/yy): ")
        lecture_recess_date = datetime.strptime(lecture_recess_text,
                                                "%d/%m/%y").date()

        # add O Week event (1 week before Week 1)
        event = Event()
        event.add('summary', study_period + ' O Week')
        event.add('dtstart', week1date - timedelta(days=7))
        cal.add_component(event)

        # loop through all numbered weeks
        week_date = week1date
        week_number = 1
        for i in range(WEEKS_IN_STUDY_PERIOD + 1):
            event = Event()
            # handle lecture recess, not incrementing week number
            if week_date == lecture_recess_date:
                event.add('summary', study_period + ' Lecture Recess')
            else:
                event.add('summary',
                          study_period + ' Week ' + str(week_number))
                week_number += 1

            event.add('dtstart', week_date)
            cal.add_component(event)
            # add one week for next event
            week_date += timedelta(days=7)

        # add swotvac and exams after final week
        event = Event()
        event.add('summary', study_period + ' Swotvac')
        event.add('dtstart', week_date)
        week_date += timedelta(days=7)
        cal.add_component(event)

        event = Event()
        event.add('summary', study_period + ' Exams')
        event.add('dtstart', week_date)
        cal.add_component(event)

    # write calendar file to disk (open the file to add events to Calendar program)
    calendar_file = open(FILE_NAME, 'wb')
    calendar_file.write(cal.to_ical())
    calendar_file.close()


