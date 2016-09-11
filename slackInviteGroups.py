"""
Script to invite students to Slack private groups for group work
Takes CSV file in the same format as that needed for CATME: http://catme.org
Match the team names in the CATME file with the private group names for Slack
Specify the email address for any staff to be added to all groups
"""
# TODO: check on creating group (if doesn't exist, create it)
# https://api.slack.com/methods/groups.create

import csv
from pprint import PrettyPrinter
from slacker import Slacker

from private import SLACK_AUTH_TOKEN
from slackFunctions import get_slack_channels, get_slack_users

__author__ = 'Lindsay Ward'

STUDENT_FILE = "data/CP1406-CATME-Teams.csv"


def main():
    slack = Slacker(SLACK_AUTH_TOKEN)
    pp = PrettyPrinter(indent=4)

    # get all students and subjects they do
    groups_students = get_group_lists(STUDENT_FILE)
    pp.pprint(groups_students)
    return

    # get users from Slack
    slack_user_details = get_slack_users(slack, pp)

    # get channels (names and ids)
    channel_details = get_slack_channels(slack)
    # pp.pprint(channel_details)

    missing = []
    invited_count = 0
    # now we can find students not in their subject channels
    for email, subjects in groups_students.items():
        try:
            slack_id = slack_user_details[email][0]
            # print(slack_id, email)
        except KeyError:
            missing.append(email)
            continue
        for subject in subjects:
            channel = subject_to_channel(subject)
            try:
                if slack_id not in channel_details[channel][1]:
                    print("inviting", email, "to", channel)
                    invited_count += 1
                    try:
                        slack.channels.invite(channel_details[channel][0], slack_id)
                    except:
                        print("ERROR with Slack call, probably missing channel for {}\n".format(channel))
            except:
                print("ERROR with lookup, probably missing channel for {}\n".format(channel))

    print("Invited people {} times".format(invited_count))
    print("\n{} people not in Slack:\n{}".format(len(missing), "\n".join(missing)))
    # output text file with missing students in form ready for bulk Slack invite (comma separated)
    with open("nonslackers.txt", "w") as f:
        f.write(", ".join(missing))


def get_group_lists(filename='allcpstudents.xlsx'):
    """
    Read CSV file saved in format for CATME, create groups of students as dictionary
    :param filename: name of groups list file to read
    :return: dictionary of {group name: set(student emails)}
    """
    # map student emails to list of subjects in a dictionary (campus doesn't matter)
    groups_of_students = {}
    input_file = open(filename, 'r')
    csv_reader = csv.reader(input_file)
    # get header row in lowercase
    header = [column.lower() for column in next(csv_reader, None)]
    # print(header)
    column_email = header.index('email')
    column_group = header.index('team')
    column_first_name = header.index('first')
    column_last_name = header.index('last')
    # print("Email: {}, Team: {}, Name: {} {}".format(column_email, column_group, column_first_name, column_last_name))

    for row in csv_reader:
        # print(row)
        group = row[column_group]
        email = row[column_email]
        name = "{} {}".format(row[column_first_name], row[column_last_name])
        # print(group, name, email)

        # update existing group's list, or add student to dictionary if not already there
        try:
            groups_of_students[group].append(email)
        except KeyError:
            groups_of_students[group] = [email]

    input_file.close()
    return groups_of_students


def test_get_students(pp):
    # get all students and subjects they do
    student_details = get_group_lists(STUDENT_FILE)
    pp.pprint(student_details)


if __name__ == '__main__':
    main()
