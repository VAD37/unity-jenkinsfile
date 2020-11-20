import os
import subprocess
import sys
from shutil import copyfile
from pathlib import Path

sys.path.insert(1, os.path.join(sys.path[0], '..'))

import Config

project_folder = Config.read(Config.KEY.UNITY_PROJECT)
version = Config.read(Config.KEY.RELEASE_VERSION)
unity_path = Config.read(Config.KEY.UNITY_PATH)
unity_version = Config.read(Config.KEY.UNITY_VERSION)
commit_hash = Config.read(Config.KEY.GIT_COMMIT_HASH)
branch = os.environ.get("BRANCH_NAME", None)
build_id = os.environ.get("BUILD_ID", None)



build_folder = os.path.join(project_folder, "build")

job_name = os.environ["JOB_NAME"].split("/")[0]

develop_folder = f"ProjectBuilds/{job_name}/develop"
android_release_folder = f"ProjectBuilds/{job_name}/release/Android/{version}"
ios_release_folder = f"ProjectBuilds/{job_name}/release/iOS/{version}"


def shell(command):
    return subprocess.run(command, stdout=subprocess.PIPE, shell=True).stdout.decode('utf-8')


def backup_file(file_path: str, cloud_des: str):
    shell(f'rclone --config {os.environ.get("NEXTCLOUD_RCLONE_CONFIG")} --auto-confirm --no-check-certificate -P copy {file_path} nextcloud:"{cloud_des}"')

# rclone --config .\rclone-config.conf --auto-confirm --no-check-certificate -P copy .\file  nextcloud:"ProjectBuilds/Project WithSpace d/release"


# Scrap all files in /build and copy them to Backup Folder
for file_name in os.listdir(build_folder):
    print("Found file: " + file_name)
    file_path = os.path.join(build_folder, file_name)
    
    if file_name.endswith(".apk"):
        backup_file(file_path, f'{develop_folder}/{file_name}')

    # Send aab + symbol zip to release folder.
    if file_name.endswith(".aab") or file_name.endswith(".symbols.zip"):
        backup_file(file_path, f'{android_release_folder}/{file_name}')
