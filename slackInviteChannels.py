"""
Script to invite all students in class list file to the Slack channels for each subject they do
Takes unedited XLSX file from JCU StaffOnline (subject "CP%"), download the file,
then use Excel to save it as an XLSX file.
"""
import openpyxl
from pprint import PrettyPrinter
from slacker import Slacker

from private import SLACK_AUTH_TOKEN
from slackFunctions import get_slack_channels, get_slack_users

NONSLACKERS_FILE = "output/nonslackers.txt"

__author__ = 'Lindsay Ward'

SUBJECT_SUBSTITUTIONS = {'CP3413': 'CP2403', 'CP3404': 'CP3302',
                         'CP5046': 'CP3046', 'CP5047': 'CP3047',
                         'CP5307': 'CP3406', 'CP3307': 'CP3406',
                         'CP5603': 'CP3302', 'CP5604': 'CP2412',
                         'CP2020': 'CP2412', 'CP5638': 'CP1406',
                         'CP5608': 'CP2411', 'CP3403': 'CP3300',
                         'CP5631': 'CP1402', 'CP5633': 'CP2402',
                         'CP5634': 'CP3300', 'CP5635': 'CP2405',
                         'CP5637': 'CP3402', 'CP5632': 'CP1404',
                         'CP2011': 'CP2406', 'CP5310': 'CP3003',
                         'CP5607': 'CP3301', 'CP5639': 'CP1401',
                         'CP5080': 'honours', 'CP5090': 'honours',
                         'CP3000': 'specialtopics', 'CP5330': 'specialtopics',
                         'CP5340': 'specialtopics', 'CP5170': 'specialtopics',
                         'CP5030': 'specialtopics', 'CP5035': 'specialtopics',
                         'CP3101': 'wil', 'CP3102': 'wil', 'CP3103': 'wil'}

STUDENT_FILE = 'data/allcpstudents.xlsx'
EXCEL_FIELD_LAST_NAME = 2
EXCEL_FIELD_EMAIL = 6
EXCEL_FIELD_SUBJECT = 11
EXCEL_FIELD_EXTERNAL = 9  # course is external (not just subject)


def main():
    slack = Slacker(SLACK_AUTH_TOKEN)
    pp = PrettyPrinter(indent=4)

    # get all students and subjects they do
    student_details, all_subjects = get_student_data(STUDENT_FILE)
    # pp.pprint(student_details)

    # get users from Slack
    slack_user_details = get_slack_users(slack, pp)

    # get channels (names and ids)
    channel_details = get_slack_channels(slack)
    # pp.pprint(channel_details)

    missing_students = []
    missing_channels = set()
    invited_count = 0
    # now we can find students not in their subject channels
    for email, subjects in student_details.items():
        try:
            slack_id = slack_user_details[email][0]
            # print(slack_id, email)
        except KeyError:
            missing_students.append(email)
            continue
        for subject in subjects:
            channel = subject_to_channel(subject)
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


def subject_to_channel(subject):
    """
    Convert subject to Slack channel name, including substituting for shared channels
    :param subject: original subject name to convert, e.g. "CP1804"
    :return: Slack channel name, e.g. "cp1404"
    """
    # replace piggyback/diploma subject codes with channel names
    if subject.startswith("CP18"):
        subject = "CP14" + subject[4:]
    elif subject.startswith("CP4"):
        subject = "honours"
    elif subject in SUBJECT_SUBSTITUTIONS:
        subject = SUBJECT_SUBSTITUTIONS[subject]
    return subject.lower()


def get_student_data(filename='allcpstudents.xlsx'):
    """
    Read Excel (XLSX) file exported from JCU StaffOnline and get all students and their subjects
    :param filename: name of class list file to read
    :return: dictionary of {email: set(subjects)} (subjects includes "external" if their course is external)
    """
    class_workbook = openpyxl.load_workbook(filename)
    class_sheet = class_workbook.get_sheet_by_name("Sheet1")
    # map student emails to list of subjects in a dictionary (campus doesn't matter)
    students = {}
    all_subjects = set()
    # first row is header, last row is total
    for i in range(1, class_sheet.max_row - 1):
        # convert cells to text in those cells (.value)
        cell_text = [cell.value for cell in class_sheet.rows[i]]
        # print(cell_text)
        # accommodate students with no first name
        if cell_text[EXCEL_FIELD_LAST_NAME] is None:
            cell_text[EXCEL_FIELD_LAST_NAME] = ""
        # name = "{} {}".format(cell_text[2], cell_text[1])
        email = cell_text[EXCEL_FIELD_EMAIL]
        subject = cell_text[EXCEL_FIELD_SUBJECT]
        # print(name, subject, campus)

        # build set of unique subjects
        all_subjects.add(subject)

        # update existing student's subjects set, or add student to dictionary if not already there
        try:
            students[email].add(subject)
        except KeyError:
            students[email] = {subject}  # creates set with one value

        # add "external" as subject for any students whose course is external
        if cell_text[EXCEL_FIELD_EXTERNAL] == "EXT":
            students[email].add("external")
        # add "sprint" channel for students in Design Thinking, only if not external
        elif subject in ["CP1403", "CP2408", "CP3405"]:
            students[email].add("sprint")

    return students, all_subjects


def check_channels(slack):
    # these = ['CP1406', 'CP1806', 'CP5632', 'CP5046', 'CP5330']
    # students, subjects = get_group_lists()
    channels = get_slack_channels(slack)
    with open("subjects.txt") as f:
        for line in f:
            s = line[:6]
            channel = subject_to_channel(s)
            if channel not in channels:
                print("ERROR", channel)


def test_get_students(pp):
    # get all students and subjects they do
    student_details, all_subjects = get_student_data(STUDENT_FILE)
    pp.pprint(student_details)


if __name__ == '__main__':
    main()

# test_get_students()
# check_channels(slack)

# Send a message
# slack.chat.post_message('#cp1404', 'Hi there. I just sent this message using the Slack API and Python! (from @lindsayward) :)')
