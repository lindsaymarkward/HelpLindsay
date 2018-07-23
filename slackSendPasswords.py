"""
Program to send passwords (could be any data) to users in Slack
input files: logins.txt like "username email"; passwords.txt like "username password"
"""
from slackclient import SlackClient
from private import SLACK_AUTH_TOKEN
from pprint import PrettyPrinter
__author__ = 'Lindsay Ward'

# TODO: This hasn't been updated for conversations API, but hasn't been used for a long time


def main():
    pp = PrettyPrinter(indent=4)
    client = SlackClient(SLACK_AUTH_TOKEN)
    emails_logins = create_login_dictionary()
    logins_passwords = create_password_dictionary()

    # get a list of all member ids
    response = client.channels.info(client.channels.get_channel_id('cp3402'))
    members = response.body['channel']['members']
    # get relevant details for just those members
    users = get_member_details(client, members)
    # pp.pprint(users)
    contacted = []
    for user_id, email in users.items():
        try:
            login = emails_logins[email]
            # print(user_id, "Your MySQL username and database on the ditwebtsv.jcu.edu.au server is {} and your password is {}".format(login, logins_passwords[login]))
            message = "Your MySQL username and database on the ditwebtsv.jcu.edu.au server is {} and your password is {}".format(login, logins_passwords[login])
            # print(message)
            # Send Slack message
            client.chat.post_message(user_id, message, as_user=True)
            contacted.append((email, login, user_id))
        except KeyError:
            print("Skipping", email)
    pp.pprint(contacted)


def create_login_dictionary():
    emails_logins = {}
    with open('logins.txt') as f:
        for line in f:
            parts = line.split()
            emails_logins[parts[1]] = parts[0]
    return emails_logins


def create_password_dictionary():
    logins_passwords = {}
    with open('data/databaseDetails.txt') as f:
        for line in f:
            parts = line.split()
            logins_passwords[parts[0]] = parts[1]
    return logins_passwords


def get_member_details(slack, members):
    member_details = {}
    response = slack.users.list()
    users = response.body['members']
    for user in users:
        if user['id'] in members:
            member_details[user['id']] = user['profile']['email']
    return member_details


main()
