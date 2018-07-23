"""
Generic (reusable) Slack functions for programs that use Slack's Python Client API
https://github.com/slackapi/python-slackclient
https://slackapi.github.io/python-slackclient/conversations.html
https://api.slack.com/methods
"""
from slackclient import SlackClient
from private import SLACK_AUTH_TOKEN, ID_LINDSAY
from pprint import PrettyPrinter

PP = PrettyPrinter(indent=4)  # used for testing and error messages


def get_slack_users(client):
    """
    Get all Slack users for a Slack team, ignoring bots and deleted users
    :param client: SlackClient API object setup for a particular Slack team
    :return: dictionary of {email: (id, username, real name)}
    """
    user_details = {}
    response = client.api_call("users.list")
    users = response['members']
    # print(len(users), "users retreived")
    for user in users:
        try:
            if user['deleted'] or user['is_bot'] or user['id'] == 'USLACKBOT':
                # print("*** {} is a bot or deleted user".format(user['name']))
                continue
            user_details[user['profile']['email']] = (
                user['id'], user['name'], user['profile']['real_name'])
        except:
            print("Error with: ")
            PP.pprint(user)
    return user_details


def get_slack_channels(client):
    """
    Get all channels from Slack team
    :param client: SlackClient API object setup for a particular Slack team
    :return: dictionary of {channel name: id}
    """
    name_to_id = {}
    response = client.api_call("conversations.list")
    channels = response['channels']
    for channel in channels:
        name_to_id[channel['name']] = channel['id']
    return name_to_id


def get_slack_channels_members(client):
    """
    Get all channels from Slack team as well as their members
    :param client: SlackClient API object setup for a particular Slack team
    :return: dictionary of {channel name: (id, [members])}
    """
    channel_details = {}
    channels = get_slack_channels(client)
    # for each channel, get its members and store them in the details dictionary
    for name, id in channels.items():
        response = client.api_call("conversations.members", channel=id, limit=999)
        members = response['members']
        channel_details[name] = (id, members)
        # print("{} members found in {}".format(len(members), name))
    return channel_details


def get_slack_groups(client):
    """
    Get all groups from a Slack team
    :param client: SlackClient API object setup for a particular Slack team
    :return: dictionary of {group name: (id, [members])}
    """
    group_details = {}
    response = client.api_call("groups.list", exclude_archived=True)
    groups = response['groups']
    for group in groups:
        group_details[group['name']] = (group['id'], group['members'])
    return group_details


def rename_groups(client, from_prefix, to_prefix):
    """Rename all groups starting with from_prefix to start with to_prefix."""
    slack_groups = get_slack_groups(client)
    for group_name, details in slack_groups.items():
        if group_name.startswith(from_prefix):
            new_name = group_name.replace(from_prefix, to_prefix)
            print(group_name, "->", new_name)
            client.api_call("groups.rename", channel=details[0], name=new_name)


def clear_purposes(client, group_ids):
    """
    Clear the purposes field of groups passed in
    :param client: SlackClient API object setup for a particular Slack team
    :param group_ids: list of group ids to clear the purposes of
    :return: None
    """
    for group_id in group_ids:
        client.api_call("groups.setPurpose", channel=group_id, purpose="")


def kick_members(client, channel_id, members, members_to_keep):
    """
    Kick all members from a channel except those marked to keep
    :param client: SlackClient API object setup for a particular Slack team
    :param channel_id: (Slack) id of group to kick members from
    :param members: set of member ids to kick (usually the current full set)
    :param members_to_keep: set of member ids to keep (not kick)
    :return:
    """
    # remove members to keep from members to kick
    to_kick = set(members) - set(members_to_keep)
    print("Kicking:", to_kick)
    for member in to_kick:
        print(member, end=' ')
        client.api_call("conversations.kick", channel=channel_id, user=member)
    print()


def test_something():
    sc = SlackClient(SLACK_AUTH_TOKEN)
    # users = get_slack_users(sc)
    # PP.pprint(users)
    # print(len(users), "users in workspace")
    # channels = get_slack_channels(sc)
    # PP.pprint(channels)
    # print(len(channels), "channels in workspace")
    # channel_details = get_slack_channels_members(sc)
    # PP.pprint(channel_details)
    # print(len(channel_details), "channels in workspace")

    # temp_channel_id = 'C5CRVCF97'
    # response = sc.api_call("conversations.members", channel=temp_channel_id)
    # members = response['members']
    # PP.pprint(members)
    # kick_members(sc, temp_channel_id, members, {ID_LINDSAY})

    # results = get_slack_groups(sc)
    # PP.pprint(results)
    # rename_groups(sc, "cool-", "test-")
    # clear_purposes(sc, ['GA0FEB1GC', 'G0CJ9THRA'])
    test_group_id = 'G0CJ9THRA'


if __name__ == '__main__':
    test_something()
