import codecs
import os
import sys

sys.path.insert(1, os.path.join(sys.path[0], '..'))

import Config
import SlackCommand


def find_errors_in_log(file):
    """
    Search through unity buildlog.txt and find common errors:
    Script/Compile error

    Build Player error like no wrong lighting , graphic API

    :param file:
    :return:
    """
    with open(file) as f:
        try:
            lines = f.readlines()
            error_lines = list()
            take_next_line = False
            for line in lines:
                if "Error building Player:" in line:
                    error_lines.append(line)

                if "-----CompilerOutput:-stdout--exitcode:" in line:
                    take_next_line = True

                if take_next_line:
                    error_lines.append(line)

                if "-----EndCompilerOutput---------------" in line:
                    take_next_line = False

            # compiler errors
            errors = ''.join(error_lines).strip()
            print(errors)
            return errors
        except Exception as e:
            print(e)
            return "failed to find error in log " + file


# Read doc https://api.slack.com/methods/files.upload

# git info
email = Config.read(Config.KEY.GIT_AUTHOR_EMAIL)
committer = Config.read(Config.KEY.GIT_COMMITER)
git_body = Config.read(Config.KEY.GIT_BODY)
git_hash = Config.read(Config.KEY.GIT_COMMIT_SHORT_HASH)
commit_time = Config.read(Config.KEY.GIT_COMMIT_DATE)


log_file = Config.read(Config.KEY.UNITY_BUILD_LOG)
find_errors_in_log(log_file)

# config
slack_channel = SlackCommand.find_user_id(email)
build_failed = Config.read(Config.KEY.UNITY_BUILD_FAILURE)
unity_project = Config.read(Config.KEY.UNITY_PROJECT)

# jenkins
pipeline_url = os.environ.get("RUN_DISPLAY_URL")
branch = os.environ.get("BRANCH_NAME")
build_id = os.environ.get("BUILD_DISPLAY_NAME")
repo = os.environ.get("WORKSPACE")

# slack stuff
mention_user = SlackCommand.get_user_mention(email)

# check Unity failure. Send Script error
if build_failed:
    print("Unity build fail. Send fail log and reaons")
    errors = find_errors_in_log(log_file)
    msg = f'''
{commit_time}
{mention_user} {build_id} - {committer} | {branch}-{git_hash}
Unity build *FAILED*
```{errors}```
Detail: {pipeline_url}'''
    # SlackCommand.send_message(slack_channel, msg)
    SlackCommand.send_file(slack_channel, log_file, f"{build_id} log", msg)
else:
    # Send UNKNOWN ERROR
    print("Failed to find error")
    msg = f'''
    {commit_time}
    {mention_user} {build_id} - {committer} | {branch}-{git_hash}
    Unity build *CRASH*
    Unknown Reason. See stacktrace for more information
    Detail: {pipeline_url}'''
    SlackCommand.send_file(slack_channel, log_file, f"{build_id} log", msg)
