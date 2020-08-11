import os, sys
import pathlib
import Config  # custom class
import platform

"""
This class generate command code for UnityBuild.ps1 and not run powershell directly. 
Because it bypass jenkins admin power and enviroment.

Also create shell command call directly with -shell argument
"""

if len(sys.argv) > 1:
    argument = sys.argv[1]
else:
    print("Missing arguments. Exit")
    exit(1)


BuildScriptName = "UnityBuild.ps1"

LogFileName = "buildlog.txt"
Logfile = os.path.join(os.getcwd(), LogFileName)

UnityBuildMethodName = "Builder.BuildDevelopment"
BuildTarget = Config.read(Config.KEY.BUILD_TARGET)
Params = ""

# create path to script and file
dir_path = os.path.dirname(os.path.realpath(__file__))
BuildScript = os.path.join(dir_path, BuildScriptName)
# assume this is Unity project folder
ProjectFolder = pathlib.Path(dir_path).parent

# save log
sys.stdout = open(os.devnull, 'w')
Config.write(Config.KEY.UNITY_BUILD_LOG, Logfile)
sys.stdout = sys.__stdout__

# Get unity path
unityPath = Config.read("UNITY_PATH")  # this one already have two quote around

pipeline = Config.read(Config.KEY.PIPELINE)

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

if "powershell" in argument:
    command = f'{BuildScript} -projectPath "{ProjectFolder}" -buildTarget {BuildTarget} -unityPath "{unityPath}" -logFile {Logfile} -executeMethod {UnityBuildMethodName}'
    if Params is not None and Params != "":
        command += f' -params "{Params}"'  # parse command that work with Window powershell
else:
    command = f'{unityPath} -quit -batchmode -projectPath "{ProjectFolder}" -buildTarget {BuildTarget} -logFile {Logfile} -executeMethod {UnityBuildMethodName}'
    if Params is not None and Params != "":
        command += f' "{Params}"'  # parse command that work with linux shell

# out put command to Jenkins
print(command)
sys.stdout.flush()  # Return string value to jenkins
