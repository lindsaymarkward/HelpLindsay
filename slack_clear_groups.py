"""
Program to clear groups by kicking out all members (except specified ones)
and clearing the purpose of the groups
"""
from pprint import PrettyPrinter
from slackclient import SlackClient
from private import SLACK_AUTH_TOKEN, members_to_keep
from slack_functions import get_slack_groups, kick_members, rename_groups

__author__ = 'Lindsay Ward'
FILENAME = "data/slackGroups.txt"
# customisation for whether or not to archive groups
ARCHIVE_GROUP = False


def main():
    # pp = PrettyPrinter(indent=4)
    client = SlackClient(SLACK_AUTH_TOKEN)
    # TODO: might be more helpful if members_to_keep was specified as emails or Slack usernames instead of Slack IDs

    group_details = get_slack_groups(client)
    # pp.pprint(group_details)

    # for testing a small number, not all in file:
    # groups_to_clear = ["cp1406-2017-team01", "cp1406-2017-team02"]
    # for group in groups_to_clear:
    groups_file = open(FILENAME, "r")
    for group in groups_file:
        group = group.strip()
        try:
            print("For {}: {}".format(group, group_details[group]))
            group_id, members = group_details[group]
            kick_members(client, group_id, members, members_to_keep)
            print("Kicking from {}".format(group))
            # set "purpose" of group to blank
            client.api_call("groups.setPurpose", channel=group_id, purpose="")
            if ARCHIVE_GROUP:
                client.api_call("groups.archive", channel=group_id)
        except Exception as error:
            print(error)
    groups_file.close()


main()


def rename():
    client = SlackClient(SLACK_AUTH_TOKEN)
    rename_groups(client, "cp3402-2017", "cp3402-2018")

# rename()
