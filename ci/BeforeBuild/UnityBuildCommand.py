import os
import sys

sys.path.insert(1, os.path.join(sys.path[0], '..'))

import pathlib
import Config  # custom class
import platform

"""
This class generate command code for bash shell and not run shell directly.
Because it bypass jenkins admin power and enviroment.
With the case of Windows. It require run through another powershell layer script to prevent bugs.
"""

LogFileName = "buildlog.txt"
Logfile = os.path.join(os.getcwd(), LogFileName)

UnityBuildMethodName = "Builder.BuildDevelopment"
BuildTarget = Config.read(Config.KEY.BUILD_TARGET)
Params = ""


# platform is very important
platform = str(platform.system()).lower()


# save log
sys.stdout = open(os.devnull, 'w')
Config.write(Config.KEY.UNITY_BUILD_LOG, Logfile)
sys.stdout = sys.__stdout__

# Get unity path
unityPath = Config.read(Config.KEY.UNITY_PATH)
ProjectFolder = Config.read(Config.KEY.UNITY_PROJECT) 

BuildMethod = Config.KEY.BUILD_METHOD_NAME

value = Config.read(BuildMethod)
if value is not None:
    UnityBuildMethodName = value

value = Config.read(Config.KEY.BUILD_TARGET)
if value is not None:
    BuildTarget = value

value = Config.read(Config.KEY.UNITY_BUILD_PARAMS)
if value is not None:
    Params = value

unityPath = unityPath.replace('"',"").replace("'","")





command = f'{unityPath} -quit -batchmode -projectPath "{ProjectFolder}" -buildTarget {BuildTarget} -logFile {Logfile} -executeMethod {UnityBuildMethodName}'
if Params is not None and Params != "":
    command += f' "{Params}"'  # parse command that work with linux shell



# Support linux non graphic component
if "linux" in platform:
    command = f"xvfb-run {command} -force-free"

Config.write("UNITY_BUILD_COMMAND", command)

# out put command to Jenkins
print(command)
sys.stdout.flush()
