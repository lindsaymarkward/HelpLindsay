"""
Generic (reusable) Slack functions for programs that use the Python Slack SDK
https://github.com/slackapi/python-slack-sdk
https://slackapi.github.io/python-slackclient/conversations.html
https://api.slack.com/methods
"""
from slack_sdk import WebClient
from private import SLACK_AUTH_TOKEN, members_to_keep
from pprint import PrettyPrinter

# from slack_invite_channels import STAFF_FILE
STAFF_FILE = 'data/slack_staff.txt'
CHANNELS_TO_CLEAR_FILENAME = 'data/channels_to_clear.txt'
PP = PrettyPrinter(indent=4)  # used for testing and error messages


def get_slack_users(client):
    """
    Get all Slack users for a Slack team, ignoring bots and deleted users
    :param client: SlackClient API object setup for a particular Slack team
    :return: dictionary of {email: (id, username, real name)}
    """
    user_details = {}
    users = []
    next_cursor = ""
    # get all users using pagination (one call won't return all)
    more_users = True
    while more_users:
        response = client.users_list(limit=500, cursor=next_cursor)
        # PP.pprint(response)
        try:
            users += response['members']
            next_cursor = response['response_metadata']['next_cursor']
            if not next_cursor:
                more_users = False
        except KeyError:
            more_users = False

    print(len(users), "users retrieved")
    for user in users:
        # PP.pprint(user)
        try:
            if user['deleted'] or user['is_bot'] or user['id'] == 'USLACKBOT':
                # print("*** {} is a bot or deleted user".format(user['name']))
                continue
            user_details[user['profile']['email']] = (
                user['id'], user['name'], user['profile']['real_name'])
        except Exception as error:
            print("Error with: {}".format(error))
            # PP.pprint(user)
    return user_details


def get_slack_channels(client):
    """
    Get all public channels from Slack team
    :param client: SlackClient API object setup for a particular Slack team
    :return: dictionary of {channel name: id}
    """
    name_to_id = {}
    channels = []
    next_cursor = ""
    # get all channels using pagination - conversations_list only returns up to `limit`
    # channels per call (default 100), so a single call can silently miss channels
    # once the workspace has more than that
    more_channels = True
    while more_channels:
        response = client.conversations_list(limit=500, cursor=next_cursor)
        # PP.pprint(response)
        try:
            channels += response['channels']
            next_cursor = response['response_metadata']['next_cursor']
            if not next_cursor:
                more_channels = False
        except KeyError:
            more_channels = False

    for channel in channels:
        name_to_id[channel['name']] = channel['id']
    return name_to_id


def get_slack_channels_members(client, channel_names=None):
    """
    Get channels from Slack team as well as their members
    :param client: SlackClient API object setup for a particular Slack team
    :param channel_names: optional iterable of channel names to restrict results to
                           (case-insensitive). Pass this whenever you only care about a
                           known subset of channels (e.g. this run's subject channels) -
                           it avoids calling conversations_members for every channel in
                           the workspace, which is often most of the API calls this
                           function makes. Leave as None to fetch every channel (slower).
    :return: dictionary of {channel name: (id, [members])}
    """
    channel_details = {}
    channels = get_slack_channels(client)
    if channel_names is not None:
        wanted_names = {name.lower() for name in channel_names}
        channels = {name: slack_id for name, slack_id in channels.items()
                    if name.lower() in wanted_names}
    # for each channel, get its members and store them in the details dictionary
    for name, slack_id in channels.items():
        response = client.conversations_members(channel=slack_id, limit=999)
        try:
            # PP.pprint(response)
            members = response['members']
            channel_details[name] = (slack_id, members)
            # print("{} members found in {}".format(len(members), name))
        except KeyError:
            print("Ignoring empty/archived channel: {}".format(name))
            # PP.pprint(response)
    return channel_details


def invite_users_to_channel(client, channel_id, user_ids, channel_name="", batch_size=100):
    """
    Invite a list/set of users to a channel, batching calls to conversations.invite.
    Slack allows up to 100 user ids per call, so this replaces what would otherwise be
    one API call per student with roughly (number of users / 100) calls per channel.
    Uses force=True so a single already-in-channel/ineligible user in a batch doesn't
    stop the rest of that batch being invited (without force=True, one bad id fails the
    whole call - see https://api.slack.com/methods/conversations.invite).
    :param client: SlackClient API object setup for a particular Slack team
    :param channel_id: Slack id of the channel to invite to
    :param user_ids: list/set of Slack user ids to invite
    :param channel_name: optional, only used to make log messages clearer
    :param batch_size: max users per API call (Slack's current limit is 100)
    :return: (invited_count, errors) - invited_count is how many were actually invited;
             errors is a list of (user_id, reason) tuples for anyone force=True skipped.
             A whole-batch failure (e.g. channel_not_found) raises SlackApiError - let
             the caller decide how to handle that (e.g. treat the channel as missing).
    """
    user_ids = list(user_ids)
    invited_count = 0
    errors = []
    for i in range(0, len(user_ids), batch_size):
        batch = user_ids[i:i + batch_size]
        response = client.conversations_invite(channel=channel_id, users=batch, force=True)
        # even with force=True, some users in the batch may not have been invited -
        # Slack reports those individually rather than failing the whole call
        failed = {err['user']: err['error'] for err in response.get('errors', [])}
        for user_id in batch:
            if user_id in failed:
                errors.append((user_id, failed[user_id]))
            else:
                invited_count += 1
    if errors:
        print("  {} user(s) not invited to {}: {}".format(
            len(errors), channel_name or channel_id, errors))
    return invited_count, errors


def get_slack_groups_members(client):
    """
    Get all groups from a Slack team
    :param client: SlackClient API object setup for a particular Slack team
    :return: dictionary of {group name: (id, [members])}
    """
    group_details = {}
    # get only private conversations (includes private groups, unlike conversations.list)
    response = client.users_conversations(types="private_channel", exclude_archived=True)
    # print(len(response['channels']))
    groups = response['channels']
    for group in groups:
        name = group['name']
        slack_id = group['id']
        try:
            response = client.conversations_members(channel=slack_id, limit=999)
            members = response['members']
            group_details[name] = (slack_id, members)
        except KeyError:
            print("Ignoring empty/archived channel: {}".format(name))
            # PP.pprint(response)
    return group_details


def rename_groups(client, from_prefix, to_prefix):
    """Rename all groups starting with from_prefix to start with to_prefix."""
    # NOTE: deprecated groups.* won't work. need admin.conversations.write... which needs Enterprise $ plan
    slack_groups = get_slack_groups_members(client)
    for group_name, details in slack_groups.items():
        if group_name.startswith(from_prefix):
            new_name = group_name.replace(from_prefix, to_prefix)
            print(group_name, "->", new_name)
            client.groups_rename(channel=details[0], name=new_name)


def clear_purposes(client, group_ids):
    """
    Clear the purposes field of groups passed in
    :param client: SlackClient API object setup for a particular Slack team
    :param group_ids: list of group ids to clear the purposes of
    :return: None
    """
    for group_id in group_ids:
        client.conversations_setPurpose(channel=group_id, purpose="")


def kick_members(client, channel_id, members, members_to_keep):
    """
    Kick members from a channel except those marked to keep
    :param client: SlackClient API object setup for a particular Slack team
    :param channel_id: (Slack) id of group to kick members from
    :param members: set of member ids to kick (usually the current full set)
    :param members_to_keep: set of member ids to keep (not kick)
    :return:
    """
    # remove members to keep from members to kick
    members_to_kick = set(members) - set(members_to_keep)
    print("Kicking:", members_to_kick)
    for member in members_to_kick:
        print(member, end=' ')
        client.conversations_kick(channel=channel_id, user=member)
    print()


def remove_students(client, all_channel_details, slack_user_details,
                    staff_filename=STAFF_FILE):
    """Remove students (not staff) from subject channels not enrolled in."""
    # First collect the staff who we want to keep in their channels
    with open(staff_filename) as staff_file:
        staff_emails = set([email.strip() for email in staff_file.readlines()])

    # filter channel dictionary to just subject and selected channels
    subject_channel_details = {name: value for name, value in
                               all_channel_details.items() if
                               name.startswith("cp")}
    subject_channel_details["sprint"] = all_channel_details.get("sprint")
    subject_channel_details["specialtopics"] = all_channel_details.get("specialtopics")
    # PP.pprint(subject_channel_details)

    staff_details = {email: details for email, details in
                     slack_user_details.items() if email in staff_emails}
    # PP.pprint(staff_details)

    # get just the staff IDs into a set
    staff_ids = set(values[0] for values in staff_details.values())

    # Temporary - only needed if clearing specific channels
    # Get list of channels from file, in case we need it for removing only specific channels
    # with open(CHANNELS_TO_CLEAR_FILENAME) as channels_file:
    #     channels_to_clear = set([channel.strip() for channel in channels_file.readlines()])

    for channel_name, channel_details in subject_channel_details.items():
        # Temporary (hack) - only remove from the following channels
        # Comment out next two lines if clearing all
        # if channel_name not in channels_to_clear:
        #     continue

        # # Temporary (hack) (TR2, when doing SP2) - Don't remove from the following channels
        # if channel_name in ["cp1401", "cp1407", "cp1409", "cp3102", "cp508090", "cp5046", "cp50467"]:
        #     continue

        channel_id = channel_details[0]
        channel_members = channel_details[1]
        count = 0
        # create set of students (all users minus the staff users)
        students_to_remove = set(channel_members) - set(staff_ids)
        # PP.pprint(students_to_remove)
        for student_id in students_to_remove:
            try:
                result = client.conversations_kick(channel=channel_id, user=student_id)
                # PP.pprint(result)
                count += 1
            except Exception as error:
                print("Error: {}".format(error))
        print("Removed {} students from {}".format(count, channel_name))


def clear_channels(client, channels_to_clear):
    """Remove all users from channels passed in."""
    channel_details = get_slack_channels_members(client)
    for channel in channels_to_clear:
        channel = channel.strip()
        try:
            print("For {}: {}".format(channel, channel_details[channel]))
            channel_id, members = channel_details[channel]
            kick_members(client, channel_id, members, members_to_keep)
            print("Kicking from {}".format(channel))
        except Exception as error:
            print(repr(error))


def delete_all_messages(client, channel_id):
    """Delete all messages found in channel/group passed in."""
    response = client.conversations_history(channel=channel_id)
    for message in response['messages']:
        ts = message['ts']
        result = client.chat_delete(channel=channel_id, ts=ts)
        if not result['ok']:
            print(result['error'])


def test_something():
    client = WebClient(token=SLACK_AUTH_TOKEN)

    # users = get_slack_users(client)
    # print(len(users))

    channels_to_clear = ["cp1401"]
    # clear_channels(client, channels_to_clear)
    delete_all_messages()
    # users = get_slack_users(sc)
    # PP.pprint(users)
    # print(len(users), "users in workspace")
    # channels = get_slack_channels(sc)
    # PP.pprint(channels)
    # print(len(channels), "channels in workspace")
    # channel_details = get_slack_channels_members(sc)
    # PP.pprint(channel_details)
    # print(len(channel_details), "channels in workspace")

    # results = get_slack_groups(sc)
    # PP.pprint(results)
    # rename_groups(sc, "cool-", "test-")
    # clear_purposes(sc, ['GA0FEB1GC', 'G0CJ9THRA'])
    # test_group_id = 'G0CJ9THRA'


if __name__ == '__main__':
    test_something()
