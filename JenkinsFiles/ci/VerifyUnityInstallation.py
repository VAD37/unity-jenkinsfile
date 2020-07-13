import os
import pathlib
import Config

"""
Find Installed Unity and save it to config
Installation will going through shell script due UnityHub limitation
"""

# cannot get this through UNITY_HUB
location = os.environ.read("UNITY_INSTALL_LOCATION", 'C:\\Program Files\\Unity\\Hub\\Editor')
unity_version = Config.read("UNITY_VERSION")

unity_version = unity_version.strip()

unity_path = os.path.join(location, unity_version, "Editor", "Unity.exe")

Config.write("UNITY_PATH", f'"{unity_path}"')

print("Check Unity Installation: " + unity_path)

unity_exe = pathlib.Path(unity_path)
if unity_exe.is_file():
    print("Confirm unity.exe exist. Return 0")
    exit(0)

print("Not found: " + unity_path)

exit(1)
