import inspect
import os
import sys
from shutil import copyfile
from pathlib import Path

currentFile = os.path.abspath(inspect.getfile(inspect.currentframe()))
currentdir = os.path.dirname(currentFile)
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

import Config

project_folder = Config.read_config(Config.KEY.UNITY_PROJECT)
version = Config.read_config(Config.KEY.RELEASE_VERSION)

build_folder = os.path.join(project_folder, "build")

job_name = os.environ["JOB_NAME"].split("/")[0]

archive_folder = os.environ["JENKINS_BUILD_ARCHIVE"]
develop_folder = os.path.join(archive_folder, job_name, "develop")

release_folder = os.path.join(archive_folder, job_name, "release")
release_folder = os.path.join(release_folder, version)
Path(release_folder).mkdir(parents=True, exist_ok=True)
Path(develop_folder).mkdir(parents=True, exist_ok=True)

for file in os.listdir(build_folder):
    print("Check File: " + file)
    # Send apk to base folder with project name

    if file.endswith(".apk"):
        apk_file= os.path.join(build_folder, file)
        new_apk_file = os.path.join(develop_folder, file)
        print(f"Copy: {apk_file} to {new_apk_file}")
        copyfile(apk_file, new_apk_file)

    # Send aab + symbol zip to release folder.
    if file.endswith(".aab"):
        aab_file= os.path.join(build_folder, file)
        new_aab_file = os.path.join(release_folder, file)
        print(f"Copy: {aab_file} to {new_aab_file}")
        copyfile(aab_file, new_aab_file)
    if "symbols.zip" in file:
        symbol_file = os.path.join(build_folder, file)
        new_symbol_file = os.path.join(release_folder, file)
        print(f"Copy: {symbol_file} to {new_symbol_file}")
        copyfile(symbol_file, new_symbol_file)



