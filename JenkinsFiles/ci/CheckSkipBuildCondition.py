import subprocess


def run_command(command):
    return subprocess.run(command, stdout=subprocess.PIPE, shell=True).stdout.decode('utf-8')


# Default skip all commit with message [skip ci]
# These commit made by build server to update changelog file


git_commit_header = run_command("git log -1 --pretty=format:%B")

if "[skip ci]" in git_commit_header or "[skipci]" in git_commit_header or "[skip-ci]" in git_commit_header or "[ci-skip]" in git_commit_header or "[ciskip]" in git_commit_header:
    print("Found skip header in commit body. Return ExitCode 1")
    exit(1)

exit(0)
