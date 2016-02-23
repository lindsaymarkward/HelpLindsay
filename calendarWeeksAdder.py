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


def create_on_campus_calendar():
    """
    Create a single calendar with one standard on-campus study period dates
    """
    # TODO: probably make this do both SP1 and SP2 in one calendar (won't really ever want just one)

    # create "calendar" to add events to
    cal = Calendar()

    study_periods = ["SP1", "SP2"]
    for study_period in study_periods:

        # get required dates - week 1 and lecture recess; others are derived
        week1text = input(study_period + " Week 1 Date (dd/mm/yy): ")
        week1date = datetime.strptime(week1text, "%d/%m/%y").date()
        lecture_recess_text = input("Lecture Recess Date (dd/mm/yy): ")
        lecture_recess_date = datetime.strptime(lecture_recess_text, "%d/%m/%y").date()

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
                event.add('summary', study_period + ' Week ' + str(week_number))
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


def create_off_campus_calendar(weeks_in_study_period=10):
    """
    Create one calendar with all 6 off-campus study periods in it
    :param weeks_in_study_period: how many weeks are in a normal study period, default = 10
    :return:
    """
    # each tuple in the list looks like (study period, week 1 date, week before lecture recess)
    start_dates = [('SP21/51', '14/03/16', 5), ('SP22/52', '18/07/16', 5), ('SP23/53', '14/11/16', 6)]

    # create "calendar" to add events to
    cal = Calendar()

    # loop through study periods (order doesn't matter)
    for study_period, start_date, lecture_recess_week in start_dates:
        print("{} starts {}, lec rec after week {}".format(study_period, start_date, lecture_recess_week))

        # loop through all numbered weeks
        week_date = datetime.strptime(start_date, "%d/%m/%y").date()
        week_number = 1
        for i in range(weeks_in_study_period + 1):
            event = Event()

            # handle lecture recess, not incrementing week number
            if i == lecture_recess_week:
                event.add('summary', study_period + ' Lecture Recess')
            else:
                event.add('summary', "{} Week {}".format(study_period, week_number))
                week_number += 1

            event.add('dtstart', week_date)
            cal.add_component(event)
            # add one week for next event
            week_date += timedelta(days=7)

    # write calendar file to disk (open the file to add events to Calendar program)
    calendar_file = open(FILE_NAME, 'wb')
    calendar_file.write(cal.to_ical())
    calendar_file.close()

create_on_campus_calendar()
# create_off_campus_calendar()
