"""
Calendar (iCalendar format) file maker for JCU Study Periods
makes a .ics file that can be imported into Calendar programs
containing the weeks in a single study period,
including Lecture Recess (specified), O week, swotvac and exams
Uses icalendar package - https://pypi.python.org/pypi/icalendar
Lindsay Ward, JCU
Started 11/12/2015
Updated for Trimesters, etc.
"""

from datetime import datetime, timedelta
from icalendar import Calendar, Event

FILE_NAME = "output/JCU_Trimesters.ics"


def main():
    """Create a single calendar with study period dates."""

    # create "calendar" to add events to
    cal = Calendar()

    # Customise the desired study periods in the string below
    # study_periods = ["SP1", "SP2"]
    study_periods = ["TR1", "TR2", "TR3"]

    for study_period in study_periods:
        # get required dates - week 1 and lecture recess; others are derived
        week_1_text = input(study_period + " Week 1 Monday Date (dd/mm/yy): ")
        week_1_date = datetime.strptime(week_1_text, "%d/%m/%y").date()
        # OLD - variable lecture recess date; now consistently after week 5
        # lecture_recess_text = input("Lecture Recess Monday Date (dd/mm/yy): ")
        # lecture_recess_date = datetime.strptime(lecture_recess_text, "%d/%m/%y").date()
        lecture_recess_date = week_1_date + timedelta(weeks=5)
        # add O Week event (1 week before Week 1)
        event = Event()
        event.add('summary', f"{study_period} O Week")
        event.add('dtstart', week_1_date - timedelta(weeks=1))
        cal.add_component(event)

        # loop through all numbered weeks
        week_date = week_1_date
        weeks_in_study_period = 10 if study_period.startswith("TR") else 13
        week_number = 1
        for _ in range(weeks_in_study_period + 1):
            event = Event()
            # handle lecture recess, not incrementing week number
            if week_date == lecture_recess_date:
                event.add('summary', f"{study_period} Lecture Recess")
            else:
                event.add('summary', f"{study_period} Week {str(week_number)}")
                week_number += 1

            event.add('dtstart', week_date)
            cal.add_component(event)
            # add one week for next event
            week_date += timedelta(weeks=1)

        # add swotvac and exams after final week
        event = Event()
        event.add('summary', f"{study_period} Swotvac")
        event.add('dtstart', week_date)
        week_date += timedelta(weeks=1)
        cal.add_component(event)

        event = Event()
        event.add('summary', f"{study_period} Exams")
        event.add('dtstart', week_date)
        cal.add_component(event)

    # write calendar file to disk (open the file to add events to Calendar program)
    with open(FILE_NAME, 'wb') as calendar_file:
        calendar_file.write(cal.to_ical())


main()
