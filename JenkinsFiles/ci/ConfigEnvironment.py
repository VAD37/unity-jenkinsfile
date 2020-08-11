import os
import pathlib
import re
import Config
import subprocess
import yaml

"""
Write Unity version to Config
"""
dir_path = os.path.dirname(os.path.realpath(__file__))

path = pathlib.Path(dir_path)
projectDir = path.parent
Config.write(Config.KEY.UNITY_PROJECT, f'"{projectDir}"')


def removeUnityTagAlias(filepath):
    """
    Name:               removeUnityTagAlias()

    Description:        Loads a file object from a Unity textual scene file, which is in a pseudo YAML style, and strips the
                        parts that are not YAML 1.1 compliant. Then returns a string as a stream, which can be passed to PyYAML.
                        Essentially removes the "!u!" tag directive, class type and the "&" file ID directive. PyYAML seems to handle
                        rest just fine after that.

    Returns:                String (YAML stream as string)


    """
    result = str()
    sourceFile = open(filepath, 'r')

    for lineNumber, line in enumerate(sourceFile.readlines()):
        if line.startswith('--- !u!'):
            result += '--- ' + line.split(' ')[2] + '\n'  # remove the tag, but keep file ID
        else:
            # Just copy the contents...
            result += line

    sourceFile.close()

    return result


# Read Project setting yalm
project_setting = removeUnityTagAlias(os.path.join(projectDir, "ProjectSettings", "ProjectSettings.asset"))
doc = yaml.safe_load(project_setting)
Config.write(Config.KEY.COMPANY_NAME, doc["PlayerSettings"]["companyName"])
Config.write(Config.KEY.PROJECT_NAME, doc["PlayerSettings"]["productName"])
# for k, v in doc["PlayerSettings"].items():
#    print(k, v)


# Read project version
project_version = os.path.join(projectDir, "ProjectSettings", "ProjectVersion.txt")
# write unity version and hash name to Config. Use them to choose unity version later
for i, line in enumerate(open(project_version)):
    for match in re.finditer("m_EditorVersion:", line):
        for m in re.finditer('(\d+)\.(\d+)\.(\w+)', line):
            Config.write(Config.KEY.UNITY_VERSION, m.group())
    for match in re.finditer("m_EditorVersionWithRevision:", line):
        for m in re.finditer('(\d+)\.(\d+)\.(\w+)', line):
            Config.write(Config.KEY.UNITY_VERSION, m.group())
        for m in re.finditer('(?<=\().+?(?=\))', line):
            Config.write(Config.KEY.UNITY_CHANGESET, m.group())

# Set Pipeline info
branch_name = os.environ["BRANCH_NAME"]
Config.write(Config.KEY.GIT_BRANCH, branch_name)
if "production" in branch_name.lower():
    Config.write(Config.KEY.PIPELINE, "production")
elif "develop" in branch_name.lower():
    Config.write(Config.KEY.PIPELINE, "development")
else:
    Config.write(Config.KEY.PIPELINE, "internal")

# from branch name name choose Build target like the agent node. This can be override by Config default
if not Config.contain(Config.KEY.BUILD_TARGET):
    if "ios" in branch_name.lower():
        Config.write(Config.KEY.BUILD_TARGET, "iOS")
    else:
        Config.write(Config.KEY.BUILD_TARGET, "Android")


# Git commit info save to Config cfg file for use in Unity.
# Unity cannot call shell to check git info
def run_command(command):
    return subprocess.run(command, stdout=subprocess.PIPE, shell=True).stdout.decode('utf-8')


def git_commit_info(format):
    return subprocess.run(f'git log -1 --pretty=format:%{format}', stdout=subprocess.PIPE, shell=True).stdout.decode(
        'utf-8')


Config.write(Config.KEY.GIT_AUTHOR_EMAIL, git_commit_info("ae"))
Config.write(Config.KEY.GIT_AUTHOR_NAME, git_commit_info("an"))
Config.write(Config.KEY.GIT_AUTHOR, git_commit_info("an"))
Config.write(Config.KEY.GIT_COMMIT_HASH, git_commit_info("H"))
Config.write(Config.KEY.GIT_COMMIT_SHORT_HASH, git_commit_info("h"))
Config.write(Config.KEY.GIT_TREE_HASH, git_commit_info("T"))
Config.write(Config.KEY.GIT_AUTHOR_DATE, git_commit_info("ai"))
Config.write(Config.KEY.GIT_COMMITER_NAME, git_commit_info("cn"))
Config.write(Config.KEY.GIT_COMMITER, git_commit_info("cn"))
Config.write(Config.KEY.GIT_COMMITER_EMAIL, git_commit_info("ce"))
Config.write(Config.KEY.GIT_COMMIT_DATE, git_commit_info("ci"))
Config.write(Config.KEY.GIT_SUBJECT, git_commit_info("s"))
Config.write(Config.KEY.GIT_BODY, git_commit_info("b"))
Config.write(Config.KEY.GIT_RAW_BODY, git_commit_info("B"))
