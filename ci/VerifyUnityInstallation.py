import os
import pathlib
import Config
import platform

"""
Find Installed Unity and save it to config
"""

# cannot get this through UNITY_HUB

platform = str(platform.system()).lower()
print("Platform: " + platform)
# Support OS X
if "darwin" in platform:
    default_unity_location = "/Applications/Unity/Hub/Editor"
elif "linux" in platform:
    default_unity_location = "~/Unity/Hub/Editor"    
else:
    default_unity_location = 'C:\\Program Files\\Unity\\Hub\\Editor'

if "darwin" in platform:
    default_unityhub_location = "/Applications/Unity Hub.app/Contents/MacOS/Unity Hub"
elif "linux" in platform:
    default_unityhub_location = "~/Unity/UnityHub.AppImage"
else:
    default_unityhub_location = 'C:\\Program Files\\Unity Hub\\Unity Hub.exe'


UNITY_HUB = os.environ.get("UNITYHUB", default_unity_location)

location = os.environ.get("UNITY_INSTALL_LOCATION", default_unity_location)
unity_version = Config.read("UNITY_VERSION")
unity_version = unity_version.strip()


print("Unity Install Location: " + location)

def check_unity_version_exist(version : str):
    if "darwin" in platform:
        unity_path = os.path.join(location, version, "Unity.app", "Contents", "MacOS", "Unity")
    elif "linux" in platform:
        unity_path = os.path.join(location, version, "Editor", "Unity")
    else:
        unity_path = os.path.join(location, version, "Editor", "Unity.exe")  

    print("Check Unity Installation: " + unity_path)
    unity_exe = pathlib.Path(unity_path)

    if unity_exe.is_file():
        Config.write("UNITY_PATH", f'"{unity_path}"')
        return True  

    print("Not found: " + unity_path)
    return False

def try_use_version(version:str):
    if( check_unity_version_exist (version)):
        print("Confirm unity.exe exist. Return 0")
        exit(0)

try_use_version(unity_version)

import re
# Find alternative version. From 2019.1.12f1 version
print("Finding alternative unity version now")
for m in re.finditer('(\d+)\.(\d+)\.', unity_version):
    print( m.group())
    possibleEditors = os.listdir(location)            
    possibleEditors.sort()
    possibleEditors.reverse()
    for f in possibleEditors:
        if( m.group() in f):
            print(f"Found alternative version: {f}")
            try_use_version(f)

exit(1)
