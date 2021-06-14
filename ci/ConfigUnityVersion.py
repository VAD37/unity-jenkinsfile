import os
import pathlib
import re
import Config

"""
Write Unity version to Config
"""
dir_path = os.path.dirname(os.path.realpath(__file__))

path = pathlib.Path(dir_path)
projectDir = path.parent
Config.save_config(Config.KEY.UNITY_PROJECT, f'"{projectDir}"')

ProjectSetting = os.path.join(projectDir, "ProjectSettings", "ProjectVersion.txt")

print(ProjectSetting)

for i, line in enumerate(open(ProjectSetting)):
    for match in re.finditer("m_EditorVersion:", line):
        for m in re.finditer('(\d+)\.(\d+)\.(\w+)', line):
            Config.save_config("UNITY_VERSION", m.group())
    for match in re.finditer("m_EditorVersionWithRevision:", line):
        for m in re.finditer('(\d+)\.(\d+)\.(\w+)', line):
            Config.save_config("UNITY_VERSION", m.group())
        for m in re.finditer('(?<=\().+?(?=\))', line):
            Config.save_config("UNITY_CHANGESET", m.group())
print("Done")
