import os
import pathlib
import Config
import platform

"""
Find Installed Unity and save it to config
"""

# cannot get this through UNITY_HUB


# Support OS X
if "Darwin" in str(platform.system()):
    default_unity_location = "/Applications/Unity/Hub/Editor"
else:
    default_unity_location = 'C:\\Program Files\\Unity\\Hub\\Editor'

if "Darwin" in str(platform.system()):
    default_unityhub_location = "/Applications/Unity Hub.app/Contents/MacOS/Unity Hub"
else:
    default_unityhub_location = 'C:\\Program Files\\Unity Hub\\Unity Hub.exe'
UNITY_HUB = os.environ.get("UNITYHUB", default_unity_location)

location = os.environ.get("UNITY_INSTALL_LOCATION", default_unity_location)
unity_version = Config.read("UNITY_VERSION")

unity_version = unity_version.strip()

if "Darwin" in str(platform.system()):
    unity_path = os.path.join(location, unity_version, "Unity.app", "Contents", "MacOS", "Unity")
else:
    unity_path = os.path.join(location, unity_version, "Editor", "Unity.exe")

Config.write("UNITY_PATH", f'"{unity_path}"')

print("Check Unity Installation: " + unity_path)

unity_exe = pathlib.Path(unity_path)
if unity_exe.is_file():
    print("Confirm unity.exe exist. Return 0")
    exit(0)

print("Not found: " + unity_path)

exit(1)
