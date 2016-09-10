"""
Generic (reusable) Slack functions for programs that use Slacker API
"""
__author__ = 'Lindsay Ward'


def get_slack_channels(slack):
    """
    Get all channels from Slack team
    :param slack: Slacker API object setup for a particular Slack team
    :return: dictionary of {name: (id, [members])}
    """
    channel_details = {}
    response = slack.channels.list()
    channels = response.body['channels']
    for channel in channels:
        channel_details[channel['name']] = (channel['id'], channel['members'])
    return channel_details


def get_slack_users(slack, pp):
    """
    Get all Slack users for a Slack team
    :param slack: Slacker API object setup for a particular Slack team
    :param pp: Pretty Printer object
    :return: dictionary of {email: (id, username, real name)}
    """
    user_details = {}
    response = slack.users.list()
    users = response.body['members']
    for user in users:
        try:
            user_details[user['profile']['email']] = (user['id'], user['name'], user['profile']['real_name'])
        except:
            print("Error with: ")
            pp.pprint(user)
    return user_details
