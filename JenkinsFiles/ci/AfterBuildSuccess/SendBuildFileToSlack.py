import os
import sys

sys.path.insert(1, os.path.join(sys.path[0], '..'))

import Config
import SlackCommand
import subprocess


def run_command(command):
    return subprocess.run(command, stdout=subprocess.PIPE, shell=True).stdout.decode('utf-8')

# git info
commit_time = run_command("git log -1 --pretty=format:%ci")
email = run_command("git log -1 --pretty=format:%ae")
committer = run_command("git log -1 --pretty=format:%cn")
git_full_message = run_command("git log -1 --pretty=format:%B")
git_hash = run_command("git log -1 --pretty=format:%h")

# config
project = Config.read(Config.KEY.PROJECT_NAME)
company = Config.read(Config.KEY.COMPANY_NAME)
slack_channel = SlackCommand.get_channel(Config.read(Config.KEY.SLACK_DEFAULT_CHANNEL))
unity_project = Config.read(Config.KEY.UNITY_PROJECT)
pipeline = Config.read(Config.KEY.PIPELINE)

# jenkins
branch = os.environ["BRANCH_NAME"]
build_id = os.environ["BUILD_NUMBER"]
pipeline_url = os.environ["RUN_DISPLAY_URL"]
build_folder = os.path.join(unity_project, "build")

# Not use function def due to function not get local variable run in jenkins
for (dirpath, dirnames, filenames) in os.walk(build_folder):
    for file in filenames:
        print(file)
        if file.endswith(".apk"):
            apk_file = os.sep.join([dirpath, file])
            print("Found: " + apk_file)
            msg = f'''\
*{company}|{project}*
{commit_time}
{build_id} - {committer} | {branch}-{git_hash}
```{git_full_message}```
Unity build *SUCCESS*
Detail: {pipeline_url}
'''
            SlackCommand.send_file(slack_channel, apk_file, f"{file}", msg)

        if file.endswith(".aab"):
            aab_file = os.sep.join([dirpath, file])
            print("Found: " + aab_file)
            msg = f'''\
*{company}|{project}*
{commit_time}
{build_id} - {committer} | {branch}-{git_hash}
```{git_full_message}```
Unity build production *SUCCESS*
Detail: {pipeline_url}
'''
            SlackCommand.send_file(slack_channel, aab_file, f"{file}", msg)
