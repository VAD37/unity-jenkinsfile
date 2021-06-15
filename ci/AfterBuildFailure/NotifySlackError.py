import codecs
import os
import sys
import traceback

sys.path.insert(1, os.path.join(sys.path[0], '..'))

import Config
import SlackCommand

# copy/paste method. TODO split into funciton if possible
def find_errors_in_log(file):
    """
    Search through unity buildlog.txt and find common errors:

    Script/Compile error
    Build Player error like no wrong lighting , graphic API
    Gradle build failed
    """    
    with open(file, encoding='utf-8') as f:
        try:
            lines = f.readlines()
            error_lines = list()

            x = 0
            lastIndex = len(lines) -1

            take_until_count = 0
            take_until_contain = ""
            take_until_emptyline = False
            while True:
                x += 1
                line = lines[x]
                if "Uploading Crash Report" in line:
                    take_until_emptyline  = True
                if "Error building Player:" in line:
                    take_until_emptyline  = True
                elif "-----CompilerOutput:-stdout--exitcode:" in line:
                    take_until_contain = "-----EndCompilerOutput---------------"
                elif "CommandInvokationFailure: Gradle build failed." in line:
                    take_until_contain = "Run with --stacktrace option to get the stack trace."
# This should not be called in batch mode.

                if take_until_contain != "":
                    error_lines.append(line)
                    if take_until_contain in line:
                        take_until_contain = ""
                elif take_until_count > 0:
                    error_lines.append(line)
                    take_until_count -= 1
                elif take_until_emptyline:
                    error_lines.append(line)
                    if line.strip() == "":
                        take_until_emptyline = False

                if x == lastIndex:
                    break


            # Group errors
            errors = ''.join(error_lines).strip()
            print(errors)
            return errors
        except Exception as e:
            import traceback
            traceback.print_exc()
            return "failed to find error in log " + file


# Read doc https://api.slack.com/methods/files.upload

# git info
email = Config.read(Config.KEY.GIT_AUTHOR_EMAIL)
committer = Config.read(Config.KEY.GIT_COMMITER)
git_body = Config.read(Config.KEY.GIT_BODY)
git_hash = Config.read(Config.KEY.GIT_COMMIT_SHORT_HASH)
commit_time = Config.read(Config.KEY.GIT_COMMIT_DATE)

log_file = Config.read(Config.KEY.UNITY_BUILD_LOG)

# config
#slack_channel = SlackCommand.find_user_id(email)
slack_channel = SlackCommand.get_channel(Config.read(Config.KEY.SLACK_DEFAULT_CHANNEL))
build_failed = Config.read(Config.KEY.UNITY_BUILD_FAILURE)
unity_project = Config.read(Config.KEY.UNITY_PROJECT)

# jenkins
pipeline_url = os.environ.get("RUN_DISPLAY_URL")
branch = os.environ.get("BRANCH_NAME")
build_id = os.environ.get("BUILD_DISPLAY_NAME")
repo = os.environ.get("WORKSPACE")

# slack stuff
mention_user = SlackCommand.get_user_mention(email)


if Config.read("UNITY_BUILD_TIMEOUT") == "TRUE":
    print("Unity build Timeout")
    msg = f'''{mention_user}
{commit_time}
{build_id} - {committer} | {branch}-{git_hash}
Unity build *TIMEOUT*
Detail: {pipeline_url}'''
    SlackCommand.send_file(slack_channel, log_file, f"{build_id} log", msg)
    # check Unity failure. Send Script error
elif build_failed:
    print("Unity build fail. Send fail log and reaons")
    errors = find_errors_in_log(log_file)
    msg = f'''{mention_user}
{commit_time}
{mention_user} {build_id} - {committer} | {branch}-{git_hash}
Unity build *FAILED*
Detail: {pipeline_url}'''
    # SlackCommand.send_message(slack_channel, msg)
    SlackCommand.send_message(slack_channel, msg)
else:
    # Send UNKNOWN ERROR
    print("Failed to find error")
    msg = f'''{mention_user}
{commit_time}
{build_id} - {committer} | {branch}-{git_hash}
Unity build *CRASH*
Unknown Reason. See stacktrace for more information
Detail: {pipeline_url}
'''
    SlackCommand.send_message(slack_channel, msg)
