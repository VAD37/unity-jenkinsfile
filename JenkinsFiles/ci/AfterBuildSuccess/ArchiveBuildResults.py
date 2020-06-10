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
unity_path = Config.read_config(Config.KEY.UNITY_PATH)

build_folder = os.path.join(project_folder, "build")

job_name = os.environ["JOB_NAME"].split("/")[0]

archive_folder = os.environ["JENKINS_BUILD_ARCHIVE"]
develop_folder = os.path.join(archive_folder, job_name, "develop")

release_folder = os.path.join(archive_folder, job_name, "release")
release_folder = os.path.join(release_folder, version)
Path(release_folder).mkdir(parents=True, exist_ok=True)
Path(develop_folder).mkdir(parents=True, exist_ok=True)

for f in os.listdir(build_folder):
    print("Check File: " + f)
    # Send apk to base folder with project name

    if f.endswith(".apk"):
        apk_file= os.path.join(build_folder, f)
        new_apk_file = os.path.join(develop_folder, f)
        print(f"Copy: {apk_file} to {new_apk_file}")
        copyfile(apk_file, new_apk_file)

    # Send aab + symbol zip to release folder.
    if f.endswith(".aab"):
        aab_file= os.path.join(build_folder, f)
        new_aab_file = os.path.join(release_folder, f)
        print(f"Copy: {aab_file} to {new_aab_file}")
        copyfile(aab_file, new_aab_file)
    if "symbols.zip" in f:
        symbol_file = os.path.join(build_folder, f)
        new_symbol_file = os.path.join(release_folder, f)
        print(f"Copy: {symbol_file} to {new_symbol_file}")
        copyfile(symbol_file, new_symbol_file)
        print("Create txt helper to know unity version when debug symbol link")
        editor_hint_file = os.path.join(build_folder, f +"." + "editor.txt")
        with open(editor_hint_file, "w") as file:
            file.write(unity_path)
        




