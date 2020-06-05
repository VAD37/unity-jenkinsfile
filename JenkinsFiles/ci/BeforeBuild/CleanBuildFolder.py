import os,sys, pathlib, shutil

dir_path = os.path.dirname(os.path.realpath(__file__))
parentdir = pathlib.Path(dir_path)
sys.path.insert(0,parentdir)

import Config


print("-----------CLEAN BUILD FOLDER-----------")

projectDir = Config.read_config(Config.KEY.UNITY_PROJECT)
buildFolder = os.path.join(projectDir, "build")

print(f"Clean folder {buildFolder}")
if(os.path.exists(buildFolder)):
    for filename in os.listdir(buildFolder):
        file_path = os.path.join(buildFolder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
                print("Unlink: " + file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
                print("Remove: " + file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


print("-----------DONE CLEAN BUILD FOLDER-----------")










print("-----------DONE CLEAN BUILD FOLDER-----------")