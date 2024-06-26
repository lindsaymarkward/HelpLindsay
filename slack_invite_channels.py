"""
Script to invite all students in class list file to the Slack channels for each subject they do
Takes unedited XLS file from JCU StaffOnline (subject "CP%", study period "SP1 or 2"), download the file
Note: for removing students from only specific channels, see

"""
import ssl
import xlrd
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.http_retry.builtin_handlers import RateLimitErrorRetryHandler

from private import SLACK_AUTH_TOKEN
from slack_functions import get_slack_channels_members, get_slack_users, PP, get_slack_channels, remove_students

DESIGN_THINKING_SUBJECTS = ["CP1403", "CP2408", "CP3405", "CP5641"]
SUBSTITUTIONS_FILE = 'data/subject_substitutions.txt'
STUDENT_FILE = 'data/Classlist_Results.xls'
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
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    client = WebClient(token=SLACK_AUTH_TOKEN, ssl=ssl_context)

    # Enable rate limited error retries (https://slack.dev/python-slack-sdk/web/index.html#retryhandler)
    rate_limit_handler = RateLimitErrorRetryHandler(max_retry_count=1)
    client.retry_handlers.append(rate_limit_handler)

    # get all students and subjects they do
    print("Getting student data from file")
    student_details, all_subjects = get_student_data(STUDENT_FILE)
    # PP.pprint(student_details)
    print("Got {} students".format(len(student_details)))

    # get users from Slack like {email: (id, username, real name)}
    print("Getting current Slack user data from workspace")
    slack_user_details = get_slack_users(client)
    # PP.pprint(slack_user_details)
    print("Got {} Slack users".format(len(slack_user_details)))

    # get channels like {channel name: (id, [members])}
    print("Getting Slack channel member details")
    channel_details = get_slack_channels_members(client)
    # PP.pprint(channel_details)

    # optionally, clear out non-enrolled students
    if WILL_REMOVE_OLD_STUDENTS:
        print("Removing all students from subject channels")
        remove_students(client, channel_details, slack_user_details, STAFF_FILE)
        # Hack: uncomment the next line if you ONLY want to remove students, so you can stop when it pauses for input.
        # input("Removed students. Press Enter to continue")

    substitutions = create_substitutions()
    missing_students = set()
    missing_channels = set()
    invited_count = 0
    # now we can find students not in their subject channels
    # TODO: (one day) You can add multiple users at once, so determine first who to add
    for email, subjects in student_details.items():
        try:
            slack_id = slack_user_details[email][0]
        except KeyError:
            missing_students.add(email)
            continue
        for subject in subjects:
            channel_name = subject_to_channel(subject, substitutions)
            try:
                channel_id = channel_details[channel_name][0]
                members = channel_details[channel_name][1]
                # print(email, slack_id, channel_name)
                # PP.pprint(channel_details[channel_name])
                if slack_id not in members:
                    print("Inviting {} to {}".format(email, channel_name))
                    invited_count += 1
                    try:
                        response = client.conversations_invite(channel=channel_id, users=[slack_id])
                    except SlackApiError as error:
                        if error.response['error'] == 'already_in_channel':
                            continue
                        if error.response['error'] == "channel_not_found":
                            missing_channels.add(channel_name)
                            continue
                        print("ERROR inviting ({})\n".format(error))
                        print(error.response)
                        input("Pausing to learn what's going on")
                        # TODO: when get a 'ratelimited' error, figure out how to get response "Retry-After:"
                        # https://github.com/slackapi/python-slack-sdk/issues/436#issuecomment-499692624
                        # (old, but time/wait is relevant)
            except Exception as error:
                print("ERROR with {} lookup ({})\n".format(channel_name, error))

    print("Invited people {} times".format(invited_count))
    print("\n{} people not in Slack:\n{}".format(len(missing_students),
                                                 ", ".join(missing_students)))
    # output text file with missing students
    # in form ready for bulk Slack invite (comma separated)
    with open(NONSLACKERS_FILE, "w") as f:
        f.write(", ".join(missing_students))
    if missing_channels:
        print("\nProblem (probably missing) channels: {}\n".format(
            "\n".join(missing_channels)))


def create_substitutions(filename=SUBSTITUTIONS_FILE):
    """Create dictionary of subject -> channel substitutions from file."""
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


def get_student_data(filename=STUDENT_FILE):
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
            channel = subject_to_channel(subject_name, substitutions)
            if channel not in channel_details:
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
