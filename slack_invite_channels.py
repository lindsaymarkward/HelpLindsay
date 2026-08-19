"""
Script to invite all students in class list file to the Slack channels for each subject they do
Takes unedited CSV file from JCU StaffOnline (subject "CP%", study period "SP1 or 2"), download the file
(OLD StaffOnline produced an XLS file; previous function get_student_data_from_xls exists.)
(Note: for removing students from only specific channels, see _channels_specific.py)
TODO: Find out why, and fix, always inviting tsv students to Townsville - check first?
"""
import csv
from collections import defaultdict

import xlrd
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.http_retry.builtin_handlers import RateLimitErrorRetryHandler

from private import SLACK_AUTH_TOKEN
from slack_functions import (get_slack_channels_members, get_slack_users, PP,
                             get_slack_channels, remove_students, invite_users_to_channel)

DESIGN_THINKING_SUBJECTS = ["CP1403", "CP2408", "CP3405", "CP5641"]
SUBSTITUTIONS_FILE = 'data/subject_substitutions.txt'
STUDENT_FILE = 'data/Classlist_Results-26-TR2.csv'
STAFF_FILE = 'data/slack_staff.txt'
NONSLACKERS_FILE = "output/nonslackers.txt"
EXCEL_FIELD_FIRST_NAME = 2
EXCEL_FIELD_EMAIL = 6
EXCEL_FIELD_SUBJECT = 11
EXCEL_FIELD_COURSE_CAMPUS = 8
EXCEL_FIELD_COURSE_MODE = 9  # course is external (not just subject)

# Customisation:
# Choose whether to remove all students from subject channels first
# For specific channels to remove students from (ONLY),
# change data/channels_to_clear.txt
# and update commented in/out slack_functions.py around where it says "Temporary (hack)"
WILL_REMOVE_OLD_STUDENTS = False


def main():
    if WILL_REMOVE_OLD_STUDENTS:
        input("Are you sure you want to remove students?! Cancel the program to stop now.")

    # make Slack API connection
    # NOTE: previously this disabled SSL certificate verification (ssl.CERT_NONE), which
    # left the connection carrying your Slack token open to man-in-the-middle interception.
    # If you were doing that to work around SSL errors, run `pip install --upgrade certifi`
    # instead of disabling verification.
    client = WebClient(token=SLACK_AUTH_TOKEN)

    # Enable rate limited error retries (https://slack.dev/python-slack-sdk/web/index.html#retryhandler)
    # max_retry_count raised from 1 to 3 - the SDK already backs off using Slack's
    # Retry-After header, and a run doing many API calls benefits from a bit more headroom.
    rate_limit_handler = RateLimitErrorRetryHandler(max_retry_count=3)
    client.retry_handlers.append(rate_limit_handler)

    # get all students and subjects they do
    print("Getting student data from file")
    student_details, all_subjects = get_student_data_from_csv(STUDENT_FILE)
    # PP.pprint(student_details)
    print(f"Got {len(student_details)} students")
    # input("STOP")
    # get users from Slack like {email: (id, username, real name)}
    print("Getting current Slack user data from workspace")
    slack_user_details = get_slack_users(client)
    # PP.pprint(slack_user_details)
    print(f"Got {len(slack_user_details)} Slack users")

    substitutions = create_substitutions()
    # work out up front which channels this run could possibly need, so we don't fetch
    # membership for every channel in the workspace (announcements, admin channels, etc.)
    needed_channels = {convert_subject_to_channel(subject, substitutions)
                       for subject in all_subjects}

    # get channels like {channel name: (id, [members])}
    print("Getting Slack channel member details")
    if WILL_REMOVE_OLD_STUDENTS:
        # remove_students() filters by its own "cp*" + extras rule, so it needs the
        # full channel list rather than just this run's subject channels
        channel_details = get_slack_channels_members(client)
    else:
        channel_details = get_slack_channels_members(client, channel_names=needed_channels)
    # PP.pprint(channel_details)

    # optionally, clear out non-enrolled students
    if WILL_REMOVE_OLD_STUDENTS:
        print("Removing all students from subject channels")
        remove_students(client, channel_details, slack_user_details, STAFF_FILE)
        # Hack: uncomment the next line if you ONLY want to remove students, so you can stop when it pauses for input.
        # input("Removed students. Press Enter to continue")

    missing_students = set()
    missing_channels = set()
    invited_count = 0

    # Pass 1: work out who needs inviting where, grouped by channel (not one API call
    # per student - a set also naturally de-duplicates students whose subjects share a
    # channel, e.g. via substitutions)
    invites_by_channel = defaultdict(set)
    for email, subjects in student_details.items():
        try:
            slack_id = slack_user_details[email][0]
        except KeyError:
            missing_students.add(email)
            continue
        for subject in subjects:
            channel_name = convert_subject_to_channel(subject, substitutions)
            channel_entry = channel_details.get(channel_name)
            if channel_entry is None:
                missing_channels.add(channel_name)
                continue
            _channel_id, members = channel_entry
            if slack_id in members:
                # Debug
                # print(f"{email} is already in {channel_name}")
                continue
            invites_by_channel[channel_name].add(slack_id)

    # Pass 2: invite everyone in batches of up to 100 per channel (Slack's limit for
    # conversations.invite), instead of one call per student per subject
    for channel_name, user_ids in invites_by_channel.items():
        channel_id = channel_details[channel_name][0]
        print(f"Inviting {len(user_ids)} student(s) to {channel_name}")
        try:
            count, errors = invite_users_to_channel(
                client, channel_id, user_ids, channel_name=channel_name)
            invited_count += count
            for user_id, reason in errors:
                if reason != 'already_in_channel':
                    print(f"  Could not invite {user_id} to {channel_name}: {reason}")
        except SlackApiError as error:
            error_code = error.response.get('error') if error.response else str(error)
            if error_code == 'channel_not_found':
                missing_channels.add(channel_name)
            else:
                print(f"ERROR inviting batch to {channel_name}: ({error})\n")
                print(error.response)

    print(f"Invited people {invited_count} times\n")
    print(f"{len(missing_students)} people not in Slack:")
    # print(", ".join(missing_students))
    # Output text file with missing students in form ready for bulk Slack invite (comma separated)
    with open(NONSLACKERS_FILE, "w") as outfile:
        outfile.write(", ".join(missing_students))
    if missing_channels:
        print("\nProblem (probably missing) channels: {}\n".format(
            "\n".join(missing_channels)))


def create_substitutions(filename=SUBSTITUTIONS_FILE):
    """Create dictionary of subject -> channel substitutions from file."""
    substitutions = {}
    with open(filename) as infile:
        for line in infile:
            subject, subject_channel = line.split()
            substitutions[subject] = subject_channel
    return substitutions


def convert_subject_to_channel(subject, substitutions):
    """
    Convert subject to Slack channel name, including substituting for shared channels
    :param substitutions:
    :param subject: original subject name to convert, e.g., "CP5639"
    :return: Slack channel name, e.g. "cp1401"
    """
    # replace piggyback subject codes with channel names
    if subject.startswith("CP4"):
        subject = "honours"
    elif subject in substitutions:
        subject = substitutions[subject]
    return subject.lower()


def get_student_data_from_csv(filename=STUDENT_FILE):
    """
    Read CSV file exported from JCU StaffOnline and get all students and their subjects
    :param filename: name of class list file to read
    :return: dictionary of {email: set(subjects)} (subjects includes "external" if their course is external)
             and a set of all subjects
    """
    infile = open(filename, 'r')
    reader = csv.reader(infile)
    email_to_subjects = {}
    all_subjects = set()
    # Map student emails to list of subjects in a dictionary (campus doesn't matter)
    # First row is header, last row is a normal value
    next(reader)  # Skip first row
    for row in reader:
        # print(row)
        email = row[EXCEL_FIELD_EMAIL]
        subject = row[EXCEL_FIELD_SUBJECT]
        campus = row[EXCEL_FIELD_COURSE_CAMPUS]
        # Build set of unique subjects
        all_subjects.add(subject)

        # Update existing student's subjects set, or add student to dictionary if not already there
        try:
            email_to_subjects[email].add(subject)
        except KeyError:
            email_to_subjects[email] = {subject}  # create set with one value

        # add "external" as subject for any students whose course is external
        # if row[EXCEL_FIELD_COURSE_MODE] == "EXT" or campus == "ONL":
        #     email_to_subjects[email].add("external")
        # else:
        #     # add internal students to their campus
        #     if campus == "TSV":
        #         email_to_subjects[email].add("townsville")
        #     elif campus == "CNS":
        #         email_to_subjects[email].add("cairns")
        #     # add "sprint" channel for students in Design Thinking subjects
        #     if subject in DESIGN_THINKING_SUBJECTS:
        #         email_to_subjects[email].add("sprint")
    infile.close()
    return email_to_subjects, all_subjects


def get_student_data_from_xls(filename=STUDENT_FILE):
    """
    Read Excel (XLSX) file exported from JCU StaffOnline and get all students and their subjects
    :param filename: name of class list file to read
    :return: dictionary of {email: set(subjects)} (subjects includes "external" if their course is external)
             and a set of all subjects
    """
    class_workbook = xlrd.open_workbook(filename)
    class_sheet = class_workbook.sheet_by_index(0)
    # map student emails to list of subjects in a dictionary (campus doesn't matter)
    students = {}
    all_subjects = set()
    # first row is header, last row is a normal value
    for i in range(1, class_sheet.nrows):
        row_values = class_sheet.row_values(i)
        # print(row_values)
        # accommodate students with no first name
        # if row_values[EXCEL_FIELD_FIRST_NAME] is None:
        #     row_values[EXCEL_FIELD_FIRST_NAME] = ""
        # name = "{} {}".format(row_values[2], row_values[1])
        email = row_values[EXCEL_FIELD_EMAIL]
        subject = row_values[EXCEL_FIELD_SUBJECT]
        campus = row_values[EXCEL_FIELD_COURSE_CAMPUS]
        # build set of unique subjects
        all_subjects.add(subject)

        # update existing student's subjects set, or add student to dictionary if not already there
        try:
            students[email].add(subject)
        except KeyError:
            students[email] = {subject}  # creates set with one value

        # add "external" as subject for any students whose course is external
        if row_values[EXCEL_FIELD_COURSE_MODE] == "EXT":
            students[email].add("external")
        else:
            # add internal students to their campus
            if campus == "TSV":
                students[email].add("townsville")
            elif campus == "CNS":
                students[email].add("cairns")
            # add "sprint" channel for students in Design Thinking subjects
            if subject in DESIGN_THINKING_SUBJECTS:
                students[email].add("sprint")
    return students, all_subjects


def check_channels():
    """Check for missing subject channels based on input file."""
    slack = WebClient(SLACK_AUTH_TOKEN)
    # these = ['CP1406', 'CP1806', 'CP5632', 'CP5046', 'CP5330']
    # students, subjects = get_group_lists()
    substitutions = create_substitutions()
    channel_details = get_slack_channels(slack)
    # PP.pprint(channel_details['cp1404'])
    with open("data/subjects.txt") as f:
        for line in f:
            subject_name = line[:6]
            channel = convert_subject_to_channel(subject_name, substitutions)
            if channel not in channel_details:
                print("ERROR", channel)


def test_get_students():
    # get all students and subjects they do
    student_details, all_subjects = get_student_data_from_xls(STUDENT_FILE)
    PP.pprint(student_details)


if __name__ == '__main__':
    main()

    # print(create_substitutions())
    # test_get_students()
    # check_channels()
