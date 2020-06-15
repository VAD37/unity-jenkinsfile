import codecs
import inspect
import os
import sys
import subprocess

currentFile = os.path.abspath(inspect.getfile(inspect.currentframe()))
currentdir = os.path.dirname(currentFile)
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

import Config
import SlackCommand


def run_command(command):
    return subprocess.run(command, stdout=subprocess.PIPE).stdout.decode('utf-8')


# Read doc https://api.slack.com/methods/files.upload

# git info
email = run_command("git log -1 --pretty=format:%ae")
committer = run_command("git log -1 --pretty=format:%cn")
git_subject = run_command("git log -1 --pretty=format:%s")
git_full_message = run_command("git log -1 --pretty=format:%B")
if not git_subject:
    git_subject = git_full_message
git_hash = run_command("git log -1 --pretty=format:%h")

# config
slack_build_report_channel = SlackCommand.get_channel(Config.read_config(Config.KEY.SLACK_BUILD_CHANNEL))
slack_production_channel = SlackCommand.get_channel(Config.read_config(Config.KEY.SLACK_PRODUCTION_CHANNEL))
unity_project = Config.read_config(Config.KEY.UNITY_PROJECT)
pipeline = Config.read_config(Config.KEY.PIPELINE)

# jenkins
branch = os.environ["BRANCH_NAME"]
build_id = os.environ["BUILD_NUMBER"]
pipeline_url = os.environ["RUN_DISPLAY_URL"]
build_folder = os.path.join(unity_project, "build")


# Not use function def due to function not get local variable run in jenkins
for file in os.listdir(build_folder):
    print("Check File: " + file)
    if file.endswith(".apk"):
        apk_file = os.path.join(build_folder, file)
        print("Found: " + apk_file)
        msg = f'''\
        {build_id} - {committer} | {branch}-{git_hash} | {git_subject}
        ```{git_full_message}```
        Unity build *SUCCESS*
        Detail: {pipeline_url}
        '''.format(length='multi-line', ordinal='second')
        SlackCommand.send_file(slack_build_report_channel, apk_file, f"{file}", msg)
    if file.endswith(".aab"):
        aab_file = os.path.join(build_folder, file)
        print("Found: " + aab_file)
        msg = f'''\
        {build_id} - {committer} | {branch}-{git_hash} | {git_subject}
        ```{git_full_message}```
        Unity build production *SUCCESS*
        Detail: {pipeline_url}
        GooglePlay Bundle file. Not for consumption
        '''.format(length='multi-line', ordinal='second')
        SlackCommand.send_file(slack_production_channel, aab_file, f"{file}", msg)
