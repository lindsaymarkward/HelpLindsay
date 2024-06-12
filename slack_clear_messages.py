#!python2
"""
Use slack-cleaner to clear all messages from all groups in the text file (one group name per line)
Requires: https://github.com/kfei/slack-cleaner
So: pip install slack-cleaner
NOTE: Uses old version of package, and Python 2; probably doesn't work anymore
Don't use this :)
"""
from subprocess import call
from private import SLACK_AUTH_TOKEN

__author__ = 'Lindsay Ward'
FILENAME = "data/slackGroups.txt"


def create_groups_file():
    """
    Custom function to write the groups file based on base name and number of groups
    :return:
    """
    groups_file = open(FILENAME, "a")
    for i in range(1, 37):
        print("cp1406-2016-team{:02d}".format(i), file=groups_file)

    for i in [1, 3, 4, 5, 10, 11]:
        print("cp3402-2016-team{:02d}".format(i), file=groups_file)
    groups_file.close()


def clean_all(filename=FILENAME):
    """
    Remove all messages by users and bots from each group in the groups file
    :param filename: name of file containing Slack groups
    :return:
    """
    groups_file = open(filename, "r")
    for group in groups_file:
        group = group.strip()
        call(['slack-cleaner', '--token', SLACK_AUTH_TOKEN, '--message', '--group', group, '--bot', '--perform'])
        call(['slack-cleaner', '--token', SLACK_AUTH_TOKEN, '--message', '--group', group, '--user', '*', '--perform'])
    groups_file.close()


# create_groups_file()
clean_all(FILENAME)
