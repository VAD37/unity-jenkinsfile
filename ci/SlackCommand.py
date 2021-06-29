import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

import Config

# Read doc https://api.slack.com/methods/files.upload
#https://i.imgur.com/dDIqDf2s.jpg
#slack_token = Config.read(Config.KEY.SLACK_BOT_TOKEN).strip().replace('"', "")
slack_token = os.environ.get("SLACK_BOT_TOKEN", "")
slack_client = WebClient(slack_token)
slack_default_channel = Config.read(Config.KEY.SLACK_DEFAULT_CHANNEL).replace('"', "")
iconurl = Config.read(Config.KEY.SLACK_ICON_URL).replace('"', "")
# iconurl = "https://i.imgur.com/dDIqDf2s.jpg"

def send_message(channel, msg):
    try:
        response = slack_client.chat_postMessage(channel=channel, text=msg, icon_url=iconurl)
        print(response)
    except SlackApiError as e:
        print(f"message: {e.message}, response: {e.response}")


def send_direct_message(email, msg):
    try:
        response = slack_client.chat_postMessage(channel=find_user_id(email), text=msg, icon_url=iconurl)
        print(response)
    except SlackApiError as e:
        print(f"message: {e.message}, response: {e.response}")


def send_file(channel, file_path, file_title, comment):
    try:
        response = slack_client.files_upload(channels=channel, file=file_path, title=file_title, initial_comment=comment, icon_url=iconurl)
        print(response)
    except SlackApiError as e:
        print(f"message: {e.message}, response: {e.response}")


def send_apk(channel, file_path):
    try:
        response = slack_client.files_upload(channels=channel, file=file_path, filetype="apk")
        print(response)
    except SlackApiError as e:
        print(f"message: {e.message}, response: {e.response}")


def get_channel(channel_text):
    if not channel_text:
        return "#" + channel_text.strip().replace("#", "")
    else:
        return "#" + slack_default_channel.strip().replace("#", "")


def find_user_id(email):
    response = slack_client.users_list(include_locale=True)
    for page in response:
        users = page['members']
        for user in users:
            profiles = user['profile']
            for k, v in profiles.items():
                if k == "email" and v == email:
                    user_id = user["id"]
                    return user_id


def get_user_mention(email):
    response = slack_client.users_list(include_locale=True)
    for page in response:
        users = page['members']
        for user in users:
            profiles = user['profile']
            for k, v in profiles.items():
                if k == "email" and v == email:
                    user_id = user["id"]
                    return f"<@{user_id}>"


def get_mention_list(input: str):
    def get_mention(p):
        for k, v in p.items():
            if k == "email" or k == "real_name_normalized" or k == "display_name_normalized":
                if input in str(v).lower():
                    user_id = user["id"]
                    print(f"found: " + v)
                    return f"<@{user_id}>"
        return None

    users_found = []
    response = slack_client.users_list(include_locale=True)
    # print(response)
    for page in response:
        users = page['members']
        for user in users:
            profiles = user['profile']
            found = get_mention(profiles)
            if found is not None:
                users_found.append(found)
    print(" ".join(users_found))


