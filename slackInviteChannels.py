"""
Script to invite all students in class list file to the Slack channels for each subject they do
Takes unedited XLS file from JCU StaffOnline (subject "CP%"), download the file
"""
import xlrd
from slacker import Slacker

from private import SLACK_AUTH_TOKEN
from slackFunctions import get_slack_channels, get_slack_users, PP


DESIGN_THINKING_SUBJECTS = ["CP1403", "CP2408", "CP3405"]
SUBSTITUTIONS_FILE = 'data/subject_substitutions.txt'
STUDENT_FILE = 'data/Classlist_Results.xls'
NONSLACKERS_FILE = "output/nonslackers.txt"
EXCEL_FIELD_FIRST_NAME = 2
EXCEL_FIELD_EMAIL = 6
EXCEL_FIELD_SUBJECT = 11
EXCEL_FIELD_COURSE_CAMPUS = 8
EXCEL_FIELD_COURSE_MODE = 9  # course is external (not just subject)


def main():
    # make Slack API connection
    slack = Slacker(SLACK_AUTH_TOKEN)

    # get all students and subjects they do
    student_details, all_subjects = get_student_data(STUDENT_FILE)

    # get users from Slack
    slack_user_details = get_slack_users(slack)

    # get channels (names and ids)
    channel_details = get_slack_channels(slack)

    substitutions = create_substitutions()
    missing_students = []
    missing_channels = set()
    invited_count = 0
    # now we can find students not in their subject channels
    for email, subjects in student_details.items():
        try:
            slack_id = slack_user_details[email][0]
        except KeyError:
            missing_students.append(email)
            continue
        for subject in subjects:
            channel = subject_to_channel(subject, substitutions)
            try:
                if slack_id not in channel_details[channel][1]:
                    print("inviting", email, "to", channel)
                    invited_count += 1
                    try:
                        slack.channels.invite(channel_details[channel][0],
                                              slack_id)
                    except:
                        print(
                            "ERROR with Slack call, probably missing channel for {}\n".format(
                                channel))
                        missing_channels.add(channel)
            except:
                print(
                    "ERROR with lookup, probably missing channel for {}\n".format(
                        channel))

    print("Invited people {} times".format(invited_count))
    print("\n{} people not in Slack:\n{}".format(len(missing_students),
                                                 "\n".join(missing_students)))
    # output text file with missing students in form ready for bulk Slack invite (comma separated)
    with open(NONSLACKERS_FILE, "w") as f:
        f.write(", ".join(missing_students))
    if missing_channels:
        print("\nProblem (probably missing) channels: {}".format(
            "\n".join(missing_channels)))


def create_substitutions(filename=SUBSTITUTIONS_FILE):
    substitutions = {}
    with open(filename) as f:
        for line in f:
            subject, subject_channel = line.split()
            substitutions[subject] = subject_channel
    return substitutions


def subject_to_channel(subject, substitutions):
    """
    Convert subject to Slack channel name, including substituting for shared channels
    :param substitutions:
    :param subject: original subject name to convert, e.g. "CP1804"
    :return: Slack channel name, e.g. "cp1404"
    """
    # replace piggyback/diploma subject codes with channel names
    if subject.startswith("CP18"):
        subject = "CP14" + subject[4:]
    elif subject.startswith("CP4"):
        subject = "honours"
    elif subject in substitutions:
        subject = substitutions[subject]
    return subject.lower()


def get_student_data(filename='data/Classlist_Results.xls'):
    """
    Read Excel (XLSX) file exported from JCU StaffOnline and get all students and their subjects
    :param filename: name of class list file to read
    :return: dictionary of {email: set(subjects)} (subjects includes "external" if their course is external)
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
    slack = Slacker(SLACK_AUTH_TOKEN)
    # these = ['CP1406', 'CP1806', 'CP5632', 'CP5046', 'CP5330']
    # students, subjects = get_group_lists()
    substitutions = create_substitutions()
    channels = get_slack_channels(slack)
    with open("data/subjects.txt") as f:
        for line in f:
            s = line[:6]
            channel = subject_to_channel(s, substitutions)
            if channel not in channels:
                print("ERROR", channel)


def test_get_students():
    # get all students and subjects they do
    student_details, all_subjects = get_student_data(STUDENT_FILE)
    PP.pprint(student_details)


if __name__ == '__main__':
    main()

# print(create_substitutions())
# test_get_students()
# check_channels()

# Send a message
# slack.chat.post_message('#cp1404', 'Hi there. I just sent this message using the Slack API and Python! (from @lindsayward) :)')
