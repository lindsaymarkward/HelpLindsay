"""
Script that sends SMS messages using Telstra's API (https://dev.telstra.com/content/sms-getting-started)
Makes use of the requests library (http://docs.python-requests.org/en/latest/index.html)
You can check for replies manually, or specify a callback (at the Telstra dev website) to handle replies

Lindsay Ward
21/12/2015
"""
# Obtained these keys from the Telstra Developer Portal - https://dev.telstra.com/user/me/apps
from private import TELSTRA_CONSUMER_KEY, TELSTRA_CONSUMER_SECRET
import requests

__author__ = 'Lindsay Ward'


def main():
    access_token = get_access_token()
    smses = {"04XXXXXX": "Message to send here"}

    message_id = ""
    for number, message in smses.items():
        message_id = send_message(number, message, access_token)
        print(message_id)

    status = get_message_status(message_id, access_token)

    replies = get_reply(message_id, access_token)
    # print(replies)
    # replies will be either a single error message (dict) or a list of replies (list)
    if type(replies) == dict:
        print("No replies yet")
    else:
        for reply in replies:
            print("{content} sent at {acknowledgedTimestamp} from {from}".format(**reply))


# These functions have been converted to Python from the curl examples at the Telstra site
# (copied above the functions)

# curl -X POST \
# -H "Content-Type: application/x-www-form-urlencoded" \
# -d "client_id=$TELSTRA_CONSUMER_KEY&client_secret=$TELSTRA_CONSUMER_SECRET&grant_type=client_credentials&scope=SMS" \
# "https://api.telstra.com/v1/oauth/token"

def get_access_token():
    data = {"client_id": TELSTRA_CONSUMER_KEY, "client_secret": TELSTRA_CONSUMER_SECRET,
            "grant_type": "client_credentials", "scope": "SMS"}
    r = requests.post("https://api.telstra.com/v1/oauth/token", data)
    # print(r.text)
    return r.json()['access_token']


# curl -H "Content-Type: application/json" \
# -H "Authorization: Bearer $TOKEN" \
# -d "{\"to\":\"$RECIPIENT_NUMBER\", \"body\":\"Hello!\"}" \
# "https://api.telstra.com/v1/sms/messages"

def send_message(recipient_number, message, access_token):
    data = {"to": recipient_number, "body": message}
    headers = {"Content-Type": "application/json", "Accept": "application/json",
               "Authorization": "Bearer {}".format(access_token)}
    # print(data)
    # print(headers)
    r = requests.post("https://api.telstra.com/v1/sms/messages", json=data, headers=headers)
    # print(r.text)
    return r.json()["messageId"]


# * MESSAGE_ID value is the value returned from a previous POST https://api.telstra.com/v1/sms/messages call
# * Authorization header value should be in the format of "Bearer xxx" where xxx is access token returned
#   from a previous GET https://api.telstra.com/v1/oauth/token request.
# MESSAGE_ID="6F0B6030D7309137"
# TOKEN="<access_token>"
#
# curl -H "Authorization: Bearer $TOKEN" \
# "https://api.telstra.com/v1/sms/messages/$MESSAGE_ID/response"

def get_reply(message_id, access_token):
    url = "https://api.telstra.com/v1/sms/messages/{}/response".format(message_id)
    # print(url)
    headers = {"Authorization": "Bearer {}".format(access_token)}
    r = requests.get(url, headers=headers)
    # print(r.text)
    return r.json()


# * MESSAGE_ID value is the value returned from a previous POST https://api.telstra.com/v1/sms/messages call
# * Authorization header value should be in the format of "Bearer xxx" where xxx is access token returned
#   from a previous GET https://api.telstra.com/v1/oauth/token request.
# MESSAGE_ID="6F0B6030D7309137"
# TOKEN="<access_token>"
#
# curl -H "Authorization: Bearer $TOKEN" \
# "https://api.telstra.com/v1/sms/messages/$MESSAGE_ID"

def get_message_status(message_id, access_token):
    url = "https://api.telstra.com/v1/sms/messages/{}".format(message_id)
    # print(url)
    headers = {"Authorization": "Bearer {}".format(access_token)}
    r = requests.get(url, headers=headers)
    # print(r.text)
    return r.json()


main()
