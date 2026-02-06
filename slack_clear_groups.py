"""
Program to clear groups by kicking out all members (except specified ones)
and clearing the purpose of the groups.
For private, assignment, groups, not subject channels.
For removing from subject channels, use the normal "invite_channels" script and set the CONSTANT to True
"""
import ssl

from pprint import PrettyPrinter
from slack_sdk import WebClient
from private import SLACK_AUTH_TOKEN, members_to_keep
from slack_functions import get_slack_groups_members, get_slack_channels_members, kick_members, rename_groups, delete_all_messages

FILENAME = "data/slackGroups.txt"
# customisation for whether to archive groups
ARCHIVE_GROUP = False


def main():
    """Remove users, clear purpose and delete messages from groups."""
    pp = PrettyPrinter(indent=4)
    # make Slack API connection
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    client = WebClient(token=SLACK_AUTH_TOKEN, ssl=ssl_context)
    # TODO: would be more helpful if members_to_keep was specified as emails or Slack usernames instead of Slack IDs

    group_details = get_slack_groups_members(client)
    pp.pprint(group_details)
    input("Pausing...")

    # for testing a small number, not all in file:
    # groups_to_clear = ["cp3402-project-team18"]

    # for when all groups are in file
    with open(FILENAME, "r") as groups_file:
        groups_to_clear = [line.strip() for line in groups_file]

    for group in groups_to_clear:
        try:
            print("For {}: {}".format(group, group_details[group]))
            group_id, members = group_details[group]
            kick_members(client, group_id, members, members_to_keep)
            print("Kicking from {}".format(group))
            # set "purpose" of group to blank
            client.conversations_setPurpose(channel=group_id, purpose="")
            delete_all_messages(client, group_id)
            if ARCHIVE_GROUP:
                client.conversations_archive(channel=group_id)
        except Exception as error:
            print(repr(error))


def rename():
    client = WebClient(SLACK_AUTH_TOKEN)
    rename_groups(client, "cp3402-2020", "cp3402-2021")


def delete_messages():
    # make Slack API connection
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    client = WebClient(token=SLACK_AUTH_TOKEN, ssl=ssl_context)
    # For groups (not channels):
    # group_details = get_slack_groups_members(client)
    # with open("data/slackGroups.txt", "r") as groups_file:
    #     groups_to_clear = [line.strip() for line in groups_file]

    # For channels (not groups):
    group_details = get_slack_channels_members(client)
    with open("data/slackGroups.txt", "r") as groups_file:
        groups_to_clear = [line.strip() for line in groups_file]

    for group in groups_to_clear:
        group_id = group_details[group][0]
        print("Deleting messages from {}: {}".format(group, group_id))
        delete_all_messages(client, group_id)


main()
# delete_messages()
