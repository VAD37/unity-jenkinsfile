### Important Note how to use Jenkins Pipeline

## Commit Message Reader
Any commit contain these specific message in *header* not in body commit will trigger special script:
`[skip ci]` Abort building CI. (Use in production pipeline to upload version tag and Changelog.md)


## Unity Hub
Unity hub always stuck when install through CLI. sometime not. It is required to sometime manually install Unity + Android.
All SDK, NDK are predefined on Agent Server.

## CI script
Any extra script/function that any dev want to extent. Put them inside subfolder of `/ci/{Build Step}` to prevent change to Jenkinsfile and breaking pipeline

All current ci scripts must be put inside `{Unity project root folder}/ci` folder.
All python script expect the parent folder is Unity project root.

## Config
All variable pass through CI script are saved inside `config.cfg` file in Unity Root folder

Any variable inside config.cfg file must be in this format `StringVariable="Some value"` `NoSpaceVariable=Value` (No space between)

# Config that can override value from default script
`PRODUCTION_BUILD_METHOD_NAME=Builder.BuildDebug` Build script inside unity project. Note this can be override when use special branch like master
`DEVELOP_BUILD_METHOD_NAME=Builder.BuildDebug` Build script inside unity project. Note this can be override when use special branch like master
`INTERNAL_BUILD_METHOD_NAME=Builder.BuildDebug` Build script inside unity project. Note this can be override when use special branch like master

`BUILD_TARGET=Android` Unity build target (Standalone, Win, Win64, OSXUniversal, Linux64, iOS, Android, WebGL, XboxOne, PS4, WindowsStoreApps, Switch, tvOS)
`UNITY_BUILD_PARAMS=""` Put any extra params want to pass into unity CLI like `-force-free  -nographics -noUpm` as long as the string value must include quote to prevent break CLI arguments reader
`UNITY_MODULE="android"` The default extra Unityhub package when install new version of unity. The NDK/SDK always come with android

`SLACK_BOT_TOKEN="xoxb-something"` Slack bot token to send log and error or build to default channel
`SLACK_DEFAULT_CHANNEL=ci` Default slack channel for bot to send message

`BUILD_BASE_BUNDLE_VERSION=0` Android Bundle Code version increment after build. Change Base to current GoogleStore version to prevent automated production build have lower version.

### How pipeline work

All Jenkins pipeline do is run python stage and archive all files in `Build/`  and `unity build log.txt`
And Jenkins should **NOT** do anything special like logic or shell script. It is harder to maintain for any changes outside of pipeline scope.

All work like notification and stash .apk files are done by python script.

## What can be modified
The first 15 lines
`buildDiscarder` is automatic process to remove old logs and old artifact from builds.
`ROOT` inside environment. In case of Unity folder is not in Git root folder. Root is your subfolder lead to Folder contain /Assets/ made by Unity. If not then leave empty. (made for network multi project)
Ex: /.git root folder/Sub-folder/Assets . The root folder is Sub-folder




### Helpful link for read document

https://www.jenkins.io/doc/book/pipeline/syntax/
https://www.jenkins.io/doc/pipeline/tour/running-multiple-steps/

# Hidden Doc But most important
https://www.jenkins.io/doc/pipeline/steps/workflow-durable-task-step/
Go look inside empty Job or task on Jenkins server. They have  `Pipeline Syntax` that generated auto code for all function written in Jenkinsfile
`http://localhost:8080/jenkins/job/{pipeline-name}/pipeline-syntax/`
