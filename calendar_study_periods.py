"""
Calendar (iCalendar format) file maker for JCU Study Periods
makes a .ics file that can be imported into Calendar programs
containing the study period weeks, including Lecture Recess (specified), O week, swotvac and exams
Uses icalendar package - https://pypi.python.org/pypi/icalendar
TRANSPARENT sets the event to be transparent so that events do not block out calendar as busy
Updated for Trimesters, TR2 having 2-week lecture recess, etc.
Lindsay Ward, JCU
Started 11/12/2015
"""

from datetime import datetime, timedelta
from icalendar import Calendar, Event

FILE_NAME = "output/JCU_Trimesters.ics"
WEEKS_IN_STUDY_PERIOD = 10


def main():
    """Create a single calendar with study period dates."""

    # create "calendar" to add events to
    cal = Calendar()

    # Customise the desired study periods in the string below
    study_periods = ["TR1", "TR2", "TR3"]

    for study_period in study_periods:
        # Get required date - week 1; others are derived
        week_1_text = input(study_period + " Week 1 Monday Date (dd/mm/yy): ")
        week_1_date = datetime.strptime(week_1_text, "%d/%m/%y").date()
        # Lecture recess is now consistently after week 5
        lecture_recess_date = week_1_date + timedelta(weeks=5)
        # Add O Week event (1 week before Week 1)
        event = Event()
        event.add('summary', f"{study_period} O Week")
        event.add('dtstart', week_1_date - timedelta(weeks=1))
        event.add('transp', 'TRANSPARENT')  # So event does not show as 'busy'
        cal.add_component(event)

        # Loop through all numbered weeks
        week_date = week_1_date
        week_number = 1
        for _ in range(WEEKS_IN_STUDY_PERIOD + 1):
            event = Event()
            # Handle lecture recess, don't increment week number
            if week_date == lecture_recess_date:
                event.add('summary', f"{study_period} Lecture Recess")

                # Handle TR2 having a 2-week lecture recess, adding an extra event
                if study_period == "TR2":
                    lecture_recess_date = week_date
                    event.add('dtstart', week_date)
                    event.add('transp', 'TRANSPARENT')
                    cal.add_component(event)
                    week_date += timedelta(weeks=1)
                    event = Event()
                    event.add('summary', f"{study_period} Lecture Recess")
            else:
                event.add('summary', f"{study_period} Week {week_number}")
                week_number += 1

            event.add('dtstart', week_date)
            event.add('transp', 'TRANSPARENT')
            cal.add_component(event)
            # Add one week for next event
            week_date += timedelta(weeks=1)

        # Add swotvac and exams after final week
        event = Event()
        event.add('summary', f"{study_period} Swotvac")
        event.add('dtstart', week_date)
        event.add('transp', 'TRANSPARENT')
        week_date += timedelta(weeks=1)
        cal.add_component(event)

        event = Event()
        event.add('summary', f"{study_period} Exams")
        event.add('dtstart', week_date)
        event.add('transp', 'TRANSPARENT')
        cal.add_component(event)

    # Write calendar file to disk
    # User should open the file to import events to Calendar program
    with open(FILE_NAME, 'wb') as calendar_file:
        calendar_file.write(cal.to_ical())
    print(f"Calendar file saved to {FILE_NAME}")


main()
