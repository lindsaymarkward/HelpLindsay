"""
Script to invite students to Slack public channels for channel work
Takes CSV file in the format: email,team (with header) - same as private groups/teams (CATME)
Specify the email address for any staff to be added to all channels in the private.py file

NOTE: This is probably defunct now (and would need updating for new Slack API)
"""

import csv
from pprint import PrettyPrinter
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from private import SLACK_AUTH_TOKEN
from slack_functions import get_slack_channels_members, get_slack_users, PP
from slack_invite_groups import get_group_lists

STUDENT_FILE = "data/externals.csv"

# Configuration: set whether or not to create channels if they're not present
WILL_CREATE_CHANNELS = False


def main():
    client = WebClient(SLACK_AUTH_TOKEN)

    # get all students and their channels
    channels_students = get_group_lists(STUDENT_FILE)

    # get all users from Slack
    slack_user_details = get_slack_users(client)

    # get all channels like {'name': (channel ID, [member IDs])}
    channel_details = get_slack_channels_members(client)

    missing_students = []
    invited_count = 0

    for channel_name, students in channels_students.items():
        print("Group: {}".format(channel_name))
        # make channel if it doesn't exist
        try:
            channel_id = channel_details[channel_name][0]
        except KeyError:
            print("No {} channel.".format(channel_name))
            if WILL_CREATE_CHANNELS:
                print("Adding it now.")
                try:
                    response = client.api_call("channels.create", name=channel_name)
                    PP.pprint(response)
                    # add new channel details to current channels dictionary in same format (id, [members])
                    channel_id = response['channel']['id']
                    channel_details[channel_name] = (channel_id, [])
                except Exception as error:
                    print(error)
                    print("Creating channel {} failed. Exiting.".format(channel_name))
                    return False
            else:
                # No channel, not created, so can't add students
                continue

        # add students to channel
        for email in students:
            # get slack ID or if user is missing, keep track of them separately
            try:
                slack_id = slack_user_details[email][0]
                # print(channel, slack_id, email)
            except KeyError:
                missing_students.append(email)
                continue

            # invite students to their channels
            try:
                if slack_id not in channel_details[channel_name][1]:
                    print("Inviting {} to {}".format(email, channel_name))
                    invited_count += 1
                    try:
                        response = client.api_call("conversations.invite", channel=channel_id, users=[slack_id])
                        # PP.pprint(response)
                    except Exception as error:
                        print(repr(error))
                        print("ERROR inviting {} to {}\n".format(email, channel_name))
            except Exception as error:
                print(repr(error))
                print("ERROR with lookup, missing channel {}?\n".format(channel_name))

    print("Invited people {} times".format(invited_count))
    print("\n{} people not in Slack:\n{}".format(len(missing_students),
                                                 "\n".join(missing_students)))
    # output text file with missing students in form ready for bulk Slack invite (comma separated)
    with open("output/nonslacker_channels.txt", "w") as f:
        f.write(", ".join(missing_students))


def run_tests():
    pp = PrettyPrinter(indent=4)
    # test getting channel lists from file
    student_details = get_group_lists(STUDENT_FILE)
    pp.pprint(student_details)

    # test getting Slack channels
    client = WebClient(SLACK_AUTH_TOKEN)
    slack_channels = get_slack_channels_members(client)
    pp.pprint(slack_channels)


# run_tests()

if __name__ == '__main__':
    main()
