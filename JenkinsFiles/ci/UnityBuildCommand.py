import os, sys
import pathlib
import Config  # custom class

"""
This class generate command code for jenkins and not run powershell directly. 
Because it bypass jenkins admin power and enviroment.
"""

BuildScriptName = "UnityBuild.ps1"
LogFileName = "buildlog.txt"
UnityBuildMethodName = "Builder.BuildDebug"
BuildTarget = "Android"
Params = ""
Arguments = "-quit -batchmode"

# create path to script and file
dir_path = os.path.dirname(os.path.realpath(__file__))
BuildScript = os.path.join(dir_path, BuildScriptName)
# assume this is Unity project folder
ProjectFolder = pathlib.Path(dir_path).parent
Logfile = os.path.join(ProjectFolder, LogFileName)


# save log
sys.stdout = open(os.devnull, 'w')    
Config.write(Config.KEY.UNITY_BUILD_LOG, Logfile)
sys.stdout = sys.__stdout__

# Get unity path
unityPath = Config.read("UNITY_PATH")  # this one already have two quote around

pipeline = Config.read(Config.KEY.PIPELINE)

BuildMethod = {
    'production': Config.KEY.PRODUCTION_BUILD_METHOD_NAME,
    'develop': Config.KEY.DEVELOP_BUILD_METHOD_NAME,
    'internal': Config.KEY.INTERNAL_BUILD_METHOD_NAME
}.get(pipeline, Config.KEY.DEFAULT_BUILD_METHOD_NAME)

# Set new value of config if exist
value = Config.read(BuildMethod)
if value is not None:
    UnityBuildMethodName = value

value = Config.read(Config.KEY.BUILD_TARGET)
if value is not None:
    BuildTarget = value

value = Config.read(Config.KEY.UNITY_BUILD_PARAMS)
if value is not None:
    Params = value

value = Config.read(Config.KEY.UNITY_BUILD_ARGUMENTS)
if value is not None:
    Arguments = value

# sample command from jenkins
# def output = powershell([script:"./ci/buildAndroid.ps1 -unityPath \"${UNITY}\" -logFile \"buildlog.txt\" -method \"Builder.BuildDebug\" -addGitLog", returnStdout:true, label:"Build unity"])
# the add git log is the default arguments of BuildAndroid script

command = f'{BuildScript} -unityProject "{ProjectFolder}" -arguments "{Arguments}" -buildTarget {BuildTarget} -unityPath "{unityPath}" -logFile {LogFileName} -method {UnityBuildMethodName} -addGitLog '
if Params is not None and Params != "":
    command += f' -params "{Params}"'

# out put command to Jenkins
print(command)
sys.stdout.flush()
