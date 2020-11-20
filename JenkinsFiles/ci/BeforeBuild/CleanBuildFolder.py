import os
import shutil
import sys

sys.path.insert(1, os.path.join(sys.path[0], '..'))

import Config

print("-----------CLEAN BUILD FOLDER-----------")

projectDir = Config.read(Config.KEY.UNITY_PROJECT)
buildFolder = os.path.join(projectDir, "build")

print(f"Clean folder {buildFolder}")
if os.path.exists(buildFolder):
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
