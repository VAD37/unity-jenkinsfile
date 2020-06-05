import subprocess


def run_command(command):
    return subprocess.run(command, stdout=subprocess.PIPE).stdout.decode('utf-8')

# Default skip all commit with message [skip ci]
# These commit made by build server to update changelog file


git_commit_header = run_command("git log -1 --pretty=format:%s")
print ( git_commit_header)

if "[skip ci]" in git_commit_header:
    print ("Found skip header")
    exit(1)

exit(0)