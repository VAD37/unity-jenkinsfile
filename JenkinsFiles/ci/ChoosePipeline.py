import sys
import Config
import os

"""
Read argument (branch) from jenkins.
then return correcting pipeline variable
"""


def set_pipeline(pipe):
    sys.stdout = open(os.devnull, 'w')
    Config.write("PIPELINE", pipe)
    sys.stdout = sys.__stdout__
    print(pipe)
    sys.stdout.flush()
    exit(0)


if len(sys.argv) > 0:
    branchName = sys.argv[1]
    if "production" in branchName:
        set_pipeline("production")
    if "develop" in branchName:
        set_pipeline("develop")
    set_pipeline("internal")
exit(1)
