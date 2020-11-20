import codecs
import os
import sys
import traceback

sys.path.insert(1, os.path.join(sys.path[0], '..'))

import Config
import SlackCommand


# git info
email = Config.read(Config.KEY.GIT_AUTHOR_EMAIL)
committer = Config.read(Config.KEY.GIT_COMMITER)
git_body = Config.read(Config.KEY.GIT_BODY)
git_hash = Config.read(Config.KEY.GIT_COMMIT_SHORT_HASH)
commit_time = Config.read(Config.KEY.GIT_COMMIT_DATE)

log_file = Config.read(Config.KEY.UNITY_BUILD_LOG)

# config
slack_channel = SlackCommand.find_user_id(email)
build_failed = Config.read(Config.KEY.UNITY_BUILD_FAILURE)
unity_project = Config.read(Config.KEY.UNITY_PROJECT)

# jenkins
pipeline_url = os.environ.get("RUN_DISPLAY_URL")
branch = os.environ.get("BRANCH_NAME")
build_id = os.environ.get("BUILD_DISPLAY_NAME")
repo = os.environ.get("WORKSPACE")

mention_user = SlackCommand.get_user_mention(email)


msg = f'''{mention_user}
{commit_time}
{mention_user} {build_id} - {committer} | {branch}-{git_hash}
Publishing file failed
{pipeline_url}
'''

SlackCommand.send_message(slack_channel, msg)
