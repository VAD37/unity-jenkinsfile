import os
import pathlib
import sys
import subprocess
"""
Look in project/Build folder.
Search *.apk aab iap symbol.zip files and append them to list separated by comma (,)
"""

files = []
output =""

dir_path = os.path.dirname(os.path.realpath(__file__))
project_folder = pathlib.Path(dir_path).parent

root_folder = subprocess.run("git rev-parse --show-toplevel", stdout=subprocess.PIPE, shell=True).stdout.decode('utf-8').strip()


android_build = os.path.join(project_folder, "build")
xcode_build = os.path.join(project_folder, "build_xcode")

if os.path.exists(android_build):
    for filename in os.listdir(android_build):
        if filename.endswith(".apk") or filename.endswith(".aab") or filename.endswith(".symbols.zip"): 
            f  = (os.path.join(android_build, filename))
            file = pathlib.PurePath(f).relative_to(root_folder)            
            files.append(str(file))
            continue
if os.path.exists(xcode_build): # No need to archive ios symbol zip. We will push it through fastlane to store directly
    for filename in os.listdir(xcode_build):
        if filename.endswith(".ipa"):
            f  = (os.path.join(xcode_build, filename))
            file = pathlib.PurePath(f).relative_to(root_folder)            
            files.append(str(file))
            continue

output = ",".join(files)

print(output)
sys.stdout.flush()  # Return string value to jenkins