import sys
import os
import pathlib
import traceback

"""
Run all python script in sub dir from this script
Must pass Through Argument
"""

dir_path = os.path.dirname(os.path.realpath(__file__))
path = pathlib.Path(dir_path)


def run_execute_file(file_path, globals=None, locals=None):
    """
    Copy from Stackoverflow
    Run file python as raw text while keeping variable and path
    """
    if globals is None:
        globals = {}
    globals.update({
        "__file__": file_path,
        "__name__": "__main__",
    })
    with open(file_path, 'rb') as file:
        exec(compile(file.read(), file_path, 'exec'), globals, locals)


def run_code_in_sub_directory(sub_directory_name):
    subdir = os.path.join(path, sub_directory_name)
    run_success = True
    if os.path.exists(subdir):
        for filename in os.listdir(subdir):
            if filename.endswith(".py"):
                print(f"\033[1;33mExecute:  \033[0m {filename} ")
                try:
                    run_execute_file(os.path.join(subdir, filename))
                except Exception as e:
                    print(f"\033[1;31m[Error]   \033[0m {filename}")
                    print(e)
                    traceback.print_exc()
                    run_success = False
                if run_success:
                    print(f"\033[1;32m[Success]   \033[0m {filename}")
                print("\n")
    else:
        print("Directory not exist: " + subdir)
    return run_success


if len(sys.argv) > 1:
    success = True
    for arg in sys.argv[1:]:
        result = run_code_in_sub_directory(arg)
        if not result:
            success = False
    if not success:
        exit(1)
    exit(0)

sys.stdout.flush()