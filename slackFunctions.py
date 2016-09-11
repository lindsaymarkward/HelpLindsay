"""
Generic (reusable) Slack functions for programs that use Slacker API
"""
__author__ = 'Lindsay Ward'


def get_slack_users(slack, pp):
    """
    Get all Slack users for a Slack team, ignoring bots and deleted users
    :param slack: Slacker API object setup for a particular Slack team
    :param pp: Pretty Printer object
    :return: dictionary of {email: (id, username, real name)}
    """
    user_details = {}
    response = slack.users.list()
    users = response.body['members']
    for user in users:
        try:
            if user['deleted'] or user['is_bot']:
                # print("*** {} is a bot or deleted user".format(user['name']))
                continue
            user_details[user['profile']['email']] = (user['id'], user['name'], user['profile']['real_name'])
        except:
            print("Error with: ")
            pp.pprint(user)
    return user_details


def get_slack_channels(slack):
    """
    Get all channels from Slack team
    :param slack: Slacker API object setup for a particular Slack team
    :return: dictionary of {channel name: (id, [members])}
    """
    channel_details = {}
    response = slack.channels.list()
    channels = response.body['channels']
    for channel in channels:
        channel_details[channel['name']] = (channel['id'], channel['members'])
    return channel_details


def get_slack_groups(slack):
    """
    Get all groups from a Slack team
    :param slack: Slacker API object setup for a particular Slack team
    :return: dictionary of {group name: (id, [members])}
    """
    group_details = {}
    response = slack.groups.list()
    groups = response.body['groups']
    for group in groups:
        group_details[group['name']] = (group['id'], group['members'])
    return group_details


def clear_purposes(slack, group_ids):
    """
    Clear the purposes field of groups listed in filename
    :param slack: Slacker API object setup for a particular Slack team
    :param group_ids: set of group ids to clear
    :return: None
    """
    for group_id in group_ids:
        slack.groups.set_purpose(group_id, "")


def kick_members(slack, group_id, members, members_to_keep):
    """
    Kick all members from a group except those marked to keep
    :param slack: Slacker API object setup for a particular Slack team
    :param group_id: (Slack) id of group to kick members from
    :param members: set of member ids to kick
    :param members_to_keep: set of member ids to keep (not kick)
    :return:
    """
    # remove members to keep from members to kick
    to_kick = set(members) - members_to_keep
    for member in to_kick:
        print(member, end=' ')
        slack.groups.kick(group_id, member)
    print()
