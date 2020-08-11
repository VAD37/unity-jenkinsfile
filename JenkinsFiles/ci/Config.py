import os
import pathlib
import fileinput
import re
import sys

"""
Create default cfg file to use between normal python code and shell script code.
Shell can use source function to use cfg file
"""


class KEY(object):
    # Manual set config
    BUILD_METHOD_NAME = "BUILD_METHOD_NAME"
    UNITY_BUILD_PARAMS = "UNITY_BUILD_PARAMS"
    UNITY_BUILD_FAILURE = "UNITY_BUILD_FAILURE"
    UNITY_BUILD_LOG = "UNITY_BUILD_LOG"
    BUILD_BASE_BUNDLE_VERSION = "BUILD_BASE_BUNDLE_VERSION"
    # Slack API
    SLACK_BOT_TOKEN = "SLACK_BOT_TOKEN"
    SLACK_DEFAULT_CHANNEL = "SLACK_DEFAULT_CHANNEL"

    # Generate config env during CI
    COMPANY_NAME = "COMPANY_NAME"
    PROJECT_NAME = "PROJECT_NAME"
    UNITY_VERSION = "UNITY_VERSION"
    UNITY_CHANGESET = "UNITY_CHANGESET"
    UNITY_MODULE = "UNITY_MODULE"
    UNITY_LICENSE = "UNITY_LICENSE"
    UNITY_PATH = "UNITY_PATH"
    UNITY_PROJECT = "UNITY_PROJECT"
    BUILD_TARGET = "BUILD_TARGET"
    PIPELINE = "PIPELINE"
    # After Unity build config
    RELEASE_VERSION = "RELEASE_VERSION"
    # Git commit info
    GIT_BRANCH = "GIT_BRANCH"
    GIT_AUTHOR_EMAIL = "GIT_AUTHOR_EMAIL"  # format:%ae
    GIT_AUTHOR_NAME = "GIT_AUTHOR_NAME"  # format:%an
    GIT_AUTHOR = "GIT_AUTHOR"  # format:%an
    GIT_COMMIT_HASH = "GIT_COMMIT_HASH"  # format:%H
    GIT_COMMIT_SHORT_HASH = "GIT_COMMIT_SHORT_HASH"  # format:%h
    GIT_TREE_HASH = "GIT_TREE_HASH"  # format:%T
    GIT_AUTHOR_DATE = "GIT_AUTHOR_DATE"  # format:%aD
    GIT_COMMITER_NAME = "GIT_COMMITER_NAME"  # format:%cn
    GIT_COMMITER = "GIT_COMMITER"  # format:%cn
    GIT_COMMITER_EMAIL = "GIT_COMMITER_EMAIL"  # format:%ce
    GIT_COMMIT_DATE = "GIT_COMMIT_DATE"  # format:%ci
    GIT_SUBJECT = "GIT_SUBJECT"  # format:%s
    GIT_BODY = "GIT_BODY"  # format:%b
    GIT_RAW_BODY = "GIT_RAW_BODY"  # format:%B


dir_path = os.path.dirname(os.path.realpath(__file__))

path = pathlib.Path(dir_path)

config = os.path.join(path.parent, "config.cfg")


def contain(name):
    with open(config, 'r') as file:
        filedata = file.readlines()
    for i, x in enumerate(filedata):
        splits = x.split("=")
        if splits[0] == name:
            return True
    return False


def read(name):
    with open(config, 'r') as file:
        filedata = file.readlines()
    for i, x in enumerate(filedata):
        splits = x.split("=")
        if splits[0] == name:
            var = splits[1].rstrip()
            if var.startswith('"') and var.endswith('"'):
                var = var[1: -1]
            return var
    return None


# Config file in format Shell Config for .sh script
def write(a1 :str, a2 :str):    
    if a2 is None or a2 == "":
        return
    # if have space then wrap it around quote
    if ' ' in a2:
        a2 = a2.strip()
        if not a2.startswith('"') and not a2.endswith('"'):
            a2 = '"' + a2 + '"'


    # Read in the file
    with open(config, 'r') as file:
        filedata = file.readlines()

    found_line = False
    for i, x in enumerate(filedata):
        if not x:
            print("remove empty line at index " + i)
            filedata.pop(i)
            continue
        splits = x.split("=")

        if len(splits) != 2:
            print("Wrong format. Remove: " + x)
            filedata.pop(i)
            continue

        if splits[0] == a1:
            print("Replace " + a1 + " from " + splits[1].strip() + " to " + a2)
            filedata[i] = a1 + "=" + a2
            found_line = True
    if not found_line:
        value = a1 + "=" + a2
        print("Add new value " + value)
        filedata.append(value)
    # Write the file out again
    with open(config, 'w') as f:
        for item in filedata:
            f.write(item.rstrip() + "\n")


def print_all_config():
    print("------CONFIG------")
    with open(config, 'r') as file:
        filedata = file.readlines()
    for i, x in enumerate(filedata):
        print(x.strip())
    print("------CONFIG------")


if len(sys.argv) > 2:
    arg1 = sys.argv[1]
    arg2 = sys.argv[2]
    write(arg1, arg2)