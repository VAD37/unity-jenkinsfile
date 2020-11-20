import os
import pathlib
import re
import Config
import subprocess
import yaml


def run_init():
    unity_settings_env()
    build_target_env()
    git_info_env()


def format_unity_yaml(filepath):
    """
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


def unity_settings_env():
    """
        Write project path and project version + project name for fastlane and pipeline to work with
    """
    # Basic env to work with
    dir_path = os.path.dirname(os.path.realpath(__file__))
    path = pathlib.Path(dir_path)
    project_dir = path.parent
    Config.write(Config.KEY.UNITY_PROJECT, f'"{project_dir}"')
    # Read Project setting yalm
    project_setting = format_unity_yaml(os.path.join(project_dir, "ProjectSettings", "ProjectSettings.asset"))
    doc = yaml.safe_load(project_setting)
    Config.write(Config.KEY.COMPANY_NAME, doc["PlayerSettings"]["companyName"])
    Config.write(Config.KEY.PROJECT_NAME, doc["PlayerSettings"]["productName"])

    # Read project version
    project_version = os.path.join(project_dir, "ProjectSettings", "ProjectVersion.txt")
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




def build_target_env():
    # Set Pipeline info
    branch_name = os.environ.get("BRANCH_NAME", "")
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


def run_command(command):
    return subprocess.run(command, stdout=subprocess.PIPE, shell=True).stdout.decode('utf-8')


def git_info_env():
    # Git commit info save to Config cfg file for use in Unity.
    # Unity cannot call shell to check git info
    Config.write(Config.KEY.GIT_AUTHOR_EMAIL, run_command(f'git log -1 --pretty=format:%ae'))
    Config.write(Config.KEY.GIT_AUTHOR_NAME, run_command(f'git log -1 --pretty=format:%an'))
    Config.write(Config.KEY.GIT_AUTHOR, run_command(f'git log -1 --pretty=format:%an'))
    Config.write(Config.KEY.GIT_COMMIT_HASH, run_command(f'git log -1 --pretty=format:%H'))
    Config.write(Config.KEY.GIT_COMMIT_SHORT_HASH, run_command(f'git log -1 --pretty=format:%h'))
    Config.write(Config.KEY.GIT_TREE_HASH, run_command(f'git log -1 --pretty=format:%T'))
    Config.write(Config.KEY.GIT_AUTHOR_DATE, run_command(f'git log -1 --pretty=format:%ai'))
    Config.write(Config.KEY.GIT_COMMITER_NAME, run_command(f'git log -1 --pretty=format:%cn'))
    Config.write(Config.KEY.GIT_COMMITER, run_command(f'git log -1 --pretty=format:%cn'))
    Config.write(Config.KEY.GIT_COMMITER_EMAIL, run_command(f'git log -1 --pretty=format:%ce'))
    Config.write(Config.KEY.GIT_COMMIT_DATE, run_command(f'git log -1 --pretty=format:%ci'))
    Config.write(Config.KEY.GIT_SUBJECT, run_command(f'git log -1 --pretty=format:%s'))
    Config.write(Config.KEY.GIT_BODY, run_command(f'git log -1 --pretty=format:%b'))
    Config.write(Config.KEY.GIT_RAW_BODY, run_command(f'git log -1 --pretty=format:%B'))




run_init()