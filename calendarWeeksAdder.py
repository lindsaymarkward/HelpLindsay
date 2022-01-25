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

FILE_NAME = "output/JCU_Weeks.ics"


def main():
    """Create a single calendar with one standard on-campus study period dates."""

    # create "calendar" to add events to
    cal = Calendar()

    # study_periods = ["SP1", "SP2"]
    study_periods = ["SP1", "SP2", "TR1", "TR2", "TR3"]
    for study_period in study_periods:

        # get required dates - week 1 and lecture recess; others are derived
        week1text = input(study_period + " Week 1 Monday Date (dd/mm/yy): ")
        week_1_date = datetime.strptime(week1text, "%d/%m/%y").date()
        lecture_recess_text = input("Lecture Recess Monday Date (dd/mm/yy): ")
        lecture_recess_date = datetime.strptime(lecture_recess_text, "%d/%m/%y").date()

        # add O Week event (1 week before Week 1)
        event = Event()
        event.add('summary', study_period + ' O Week')
        event.add('dtstart', week_1_date - timedelta(days=7))
        cal.add_component(event)

        # loop through all numbered weeks
        week_date = week_1_date
        week_number = 1
        weeks_in_study_period = 10 if study_period.startswith("TR") else 13
        for i in range(weeks_in_study_period + 1):
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


main()
