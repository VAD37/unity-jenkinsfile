import sys
import os
import pathlib
import traceback
import subprocess

"""
Run all python script in sub dir from this script
Must pass Through Argument
"""

dir_path = os.path.dirname(os.path.realpath(__file__))
path = pathlib.Path(dir_path)


def run_code_in_sub_directory(dirName):
    subdir = os.path.join(path, dirName)
    if os.path.exists(subdir):
        for filename in os.listdir(subdir):
            if filename.endswith(".py"):
                print("Run Python Script: " + filename)
                try:
                    exec(open(os.path.join(subdir, filename)).read())
                except SyntaxError as e:
                    print('Failed to parse %s. Reason: %s' % (filename, e))
                    traceback.print_exc()
                except Exception as e:
                    print('Failed to execute %s. Reason: %s' % (filename, e))
                    traceback.print_exc()
                except:
                    print(filename + " Python failed unknown error")
                    traceback.print_exc()
                print("Done Execute Python Script: " + filename)
    else:
        print("Directory not exist: " + subdir)


if len(sys.argv) > 1:
    for arg in sys.argv[1:]:
        run_code_in_sub_directory(arg)

sys.stdout.flush()
