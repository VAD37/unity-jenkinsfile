import os
import pathlib
import Config
import glob
import subprocess

"""
Find unity license file and install it using Unitypath inside config
"""

dir_path = os.path.dirname(os.path.realpath(__file__))

path = pathlib.Path(dir_path).parent

logfile = os.path.join(path, "log_license.txt")

unity_path = Config.read("UNITY_PATH").strip()

license_file = None

for root, dirs, files in os.walk(path):
    for f in files:
        if f.endswith(".x.ulf"):
            license_file = (os.path.join(root, f))
            break

if license_file is None:
    print("No license file found. Ignore licensing unity")
    exit(0)

Config.write("UNITY_LICENSE", '"' + license_file + '"')

license_file = (os.path.abspath(license_file))
logfile = (os.path.abspath(logfile))

print(license_file)
print(logfile)

command = unity_path + f' -batchmode -manualLicenseFile \"{license_file}\" -logfile \"{logfile}\" '
print(command)
print("call unity install license")

result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)

print(f"ReturnCode: {result.returncode}")
print(result.stdout)
print(result.stderr)

print("")
with open(logfile, 'r') as file:
    filedata = file.readlines()
    for line in filedata:
        print(line)

# \"${UNITY}\" -manualLicenseFile \"${UNITY_LICENSE_FILE}\" -logfile \"./${UNITY_PROJECT_SUB_FOLDER}/log_license.txt\" -batchmode", returnStatus:true)
