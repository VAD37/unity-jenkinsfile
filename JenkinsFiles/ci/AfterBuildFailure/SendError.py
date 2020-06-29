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


def find_errors_in_log(file):
    first_line = 0
    last_line = 0
    with open(file, 'r') as f:
        try:
            lines = f.readlines()
            for i, x in enumerate(lines):
                if "-----CompilerOutput:-stdout--exitcode:" in x:
                    first_line = i + 3
                if "Uploading Crash Report" in x and first_line == 0:
                    first_line = i + 1
                    last_line = len(lines) - 1
                if "-----EndCompilerOutput---------------" in x:
                    last_line = i - 1
            error_lines = lines[first_line:last_line]
            errors = ''.join(error_lines).strip()
            print(errors)
            return errors
        except:
            print("failed to find error")
            return "failed to find error in log " + file


def run_command(command):
    return subprocess.run(command, stdout=subprocess.PIPE).stdout.decode('utf-8')


# Read doc https://api.slack.com/methods/files.upload

# git info
email = run_command("git log -1 --pretty=format:%ae")
committer = run_command("git log -1 --pretty=format:%cn")
git_body = run_command("git log -1 --pretty=format:%b")
git_hash = run_command("git log -1 --pretty=format:%h")

# config
slack_channel = SlackCommand.find_user_id(email)
# slack_channel = Config.read_config(Config.KEY.SLACK_ERROR_CHANNEL)
log_file = Config.read_config(Config.KEY.UNITY_BUILD_LOG)

unity_failure_file = Config.read_config(Config.KEY.UNITY_BUILD_FAILURE)
unity_project = Config.read_config(Config.KEY.UNITY_PROJECT)

# jenkins
pipeline_url = os.environ["RUN_DISPLAY_URL"]
branch = os.environ["BRANCH_NAME"]
build_id = os.environ["BUILD_DISPLAY_NAME"]
repo = os.environ["WORKSPACE"]

# slack stuff
mention_user = SlackCommand.get_user_mention(email)

# check Unity failure. Send Script error
if unity_failure_file:
    print("Unity build fail. Send fail log and reaons")
    err_file = os.path.join(unity_project, unity_failure_file)
    encoded_text = open(err_file, 'rb').read()
    bom = codecs.BOM_UTF16_LE
    encoded_text = encoded_text[len(bom):]
    filedata = encoded_text.decode('utf-16le').strip()
    errors = find_errors_in_log(log_file)

    msg = f'''\
{mention_user} {build_id} - {committer} | {branch}-{git_hash} | {git_body}
Unity build *failure*
[FILEDATA]
```{errors}```
Detail: {pipeline_url}
\
'''.format(length='multi-line', ordinal='second')

    if not filedata:
        msg.replace("[FILEDATA]", f"```{filedata}```")
    else:
        msg.replace("[FILEDATA]", "")
    # SlackCommand.send_message(slack_channel, msg)
    SlackCommand.send_file(slack_channel, log_file, f"{build_id} log", msg)
    exit(0)

# Send Build CRASH file
if not Config.has_config(Config.KEY.UNITY_BUILD_FAILURE):
    # Unity not throw build log => Crash
    print("Unity build crash.")
    errors = find_errors_in_log(log_file)
    msg = f'''\
{mention_user} {build_id} - {committer} | {branch}-{git_hash} | {git_body}
Unity build *CRASH*
```{errors}```
Detail: {pipeline_url}
'''.format(length='multi-line', ordinal='second')
    SlackCommand.send_file(slack_channel, log_file, f"{build_id} log", msg)
    exit(0)

# Send UNKNOWN ERROR
print("Failed to find error")
msg = f'''\
{mention_user} {build_id} - {committer} | {branch}-{git_hash} | {git_body}
Unity build *CRASH*
Unknown Reason. See stacktrace for more information
Detail: {pipeline_url}
'''.format(length='multi-line', ordinal='second')
SlackCommand.send_file(slack_channel, log_file, f"{build_id} log", msg)

exit(1)
