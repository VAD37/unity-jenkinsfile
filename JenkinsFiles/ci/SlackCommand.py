from slack import WebClient
from slack.errors import SlackApiError
import Config
import json

# Read doc https://api.slack.com/methods/files.upload

slack_token = Config.read_config(Config.KEY.SLACK_BOT_TOKEN).strip().replace('"', "")
slack_client = WebClient(slack_token)
slack_default_channel = Config.read_config(Config.KEY.SLACK_DEFAULT_CHANNEL).replace('"', "")
slack_ci_channel = Config.read_config(Config.KEY.SLACK_BUILD_CHANNEL).replace('"', "")
slack_log_channel = Config.read_config(Config.KEY.SLACK_ERROR_CHANNEL).replace('"', "")


def send_message(channel, msg):
    try:
        response = slack_client.chat_postMessage(channel=channel, text=msg)
        print(response)
    except SlackApiError as e:
        print(f"message: {e.message}, response: {e.response}")


def send_direct_message(email, msg):
    try:
        response = slack_client.chat_postMessage(channel=find_user_id(email), text=msg)
        print(response)
    except SlackApiError as e:
        print(f"message: {e.message}, response: {e.response}")


def send_file(channel, file_path, file_title, comment):
    try:
        response = slack_client.files_upload(channels=channel, file=file_path, title=file_title,
                                             initial_comment=comment)
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
