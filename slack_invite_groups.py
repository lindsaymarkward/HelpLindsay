"""
Script to invite students to Slack private groups for group work
Takes CSV file in the same format as that needed for CATME:
https://info.catme.org/instructor-faqhelptext-and-troubleshooting/#faq-772
Match the team names in the CATME file with the private group names for Slack
Specify the email address for any staff to be added to all groups in the private file
"""

import csv
from pprint import PrettyPrinter
from slackclient import SlackClient

from private import SLACK_AUTH_TOKEN, STAFF_TO_ADD
from slack_functions import get_slack_groups_members, get_slack_users

__author__ = 'Lindsay Ward'

STUDENT_FILE = "data/cp3402groups.csv"
# STUDENT_FILE = "data/externals.csv"

# Configuration: set whether or not to create groups if they're not present
WILL_CREATE_GROUPS = True


def main():
    client = SlackClient(SLACK_AUTH_TOKEN)
    pp = PrettyPrinter(indent=4)

    # get all students and their groups
    groups_students = get_group_lists(STUDENT_FILE)
    pp.pprint(groups_students)

    # get all users from Slack
    slack_user_details = get_slack_users(client)

    # get all groups like {'name': (group ID, [member IDs])}
    group_details = get_slack_groups_members(client)
    # pp.pprint(group_details)

    missing_students = []
    invited_count = 0

    for group_name, students in groups_students.items():
        print("Group: {}".format(group_name))
        # make group if it doesn't exist
        try:
            group_id = group_details[group_name][0]
        except KeyError:
            print("No {} group.".format(group_name))
            if WILL_CREATE_GROUPS:
                print("Adding it now.")
                try:
                    response = client.api_call("groups.create", name=group_name)
                    # add new group details to current groups dictionary in same format (id, [members])
                    group_id = response['group']['id']
                    group_details[group_name] = (group_id, [])
                except Exception as error:
                    print(error)
                    print("Creating group {} failed. Exiting.".format(group_name))
                    return False
            else:
                # No group, not created, so can't add students
                continue

        # add students to group
        for email in students:
            # get slack ID or if user is missing, keep track of them separately
            try:
                slack_id = slack_user_details[email][0]
                # print(group, slack_id, email)
            except KeyError:
                missing_students.append(email)
                continue

            # invite students to their groups
            try:
                if slack_id not in group_details[group_name][1]:
                    print("Inviting {} to {}".format(email, group_name))
                    invited_count += 1
                    try:
                        client.api_call("groups.invite", channel=group_id, user=slack_id)
                    except Exception as error:
                        print(error)
                        print("ERROR inviting {} to {}\n".format(email, group_name))
            except Exception as error:
                print(error)
                print("ERROR with lookup, missing group {}?\n".format(group_name))

    print("Invited people {} times".format(invited_count))
    print("\n{} people not in Slack:\n{}".format(len(missing_students),
                                                 "\n".join(missing_students)))
    # output text file with missing students in form ready for bulk Slack invite (comma separated)
    with open("output/nonslacker_groups.txt", "w") as f:
        f.write(", ".join(missing_students))


def get_group_lists(filename):
    """
    Read CSV file saved in format for CATME, create groups of students as dictionary
    :param filename: name of groups list file to read
    :return: dictionary of {group name: set(student emails)}
    """
    # map groups to set of emails
    groups_of_students = {}
    input_file = open(filename, 'r')
    csv_reader = csv.reader(input_file)
    # get header row in lowercase
    header = [column.lower() for column in next(csv_reader, None)]
    # print(header)
    column_email = header.index('email')
    column_group = header.index('team')
    # column_first_name = header.index('first')
    # column_last_name = header.index('last')
    # print("Email: {}, Team: {}, Name: {} {}".format(column_email, column_group, column_first_name, column_last_name))

    for row in csv_reader:
        # print(row)
        group = row[column_group]
        # skip blank groups (for unfinished data file)
        if not group:
            continue
        email = row[column_email]
        # name = "{} {}".format(row[column_first_name], row[column_last_name])
        # print(group, name, email)

        # update existing group's list,
        # or add student to new entry in dictionary if not already there
        try:
            groups_of_students[group].append(email)
        except KeyError:
            groups_of_students[group] = [email]

    # add staff members to groups
    if len(STAFF_TO_ADD) > 0:
        for group in groups_of_students:
            groups_of_students[group] += STAFF_TO_ADD
    input_file.close()
    return groups_of_students


def run_tests():
    pp = PrettyPrinter(indent=4)
    # test getting group lists from file
    student_details = get_group_lists(STUDENT_FILE)
    pp.pprint(student_details)

    # test getting Slack groups
    client = SlackClient(SLACK_AUTH_TOKEN)
    slack_groups = get_slack_groups_members(client)
    pp.pprint(slack_groups)


# run_tests()

if __name__ == '__main__':
    main()
