# Unity Jenkinsfile

Multi-branch Jenkinsfile and python script for automated **Android** build Production: Install Unity -> Build Unity -> Send Slack notification.

Made specifically for Windows Standalone Server. (Meaning no special install and setup for server. Just install jenkins setup some system variables and it will ready to go)

Read [pipeline doc](/JenkinsFiles/ci/README.md) for how to setup UnityProject builder script.

## Install in Package Manager

Add this line to `manifest.json`

`"com.vad37.unity-jenkinsfile": "https://github.com/VAD37/unity-jenkinsfile.git",`

The script will copy all files to your Unity project. Access possible unity config in `Tools/Jenkins Build`

If you manually copy them then change important *Static Variables* on top of `Jenkinsfile`

## Setup Jenkins Server

Due to limitation of Docker and Unity Linux during this project was made. It was much easier to build Unity on Windows.

**IMPORANT** must install mingw64 as bash shell in Windows. If you dont know what is Mingw is, it is the same as Git Bash.

You can install mingw64 or git bash through Chocolatey for best result.

Windows Jenkins will not run git command with any other Linux shell like Window-Linux or cygwin due to Different in window directory path.

# Enviroment Variables Requirements

**IMPORANT** Make sure git Bash or mingw64 bash.exe be on top in `Path` environment. Other linux shell command can still be accessible when use in pipeline.
After reset environment. Restart server.

![sapmple](/doc/env-path.jpg)

`JAVA_HOME` : Required for android build. Just install newest Java JDK

`UNITY_INSTALL_LOCATION` : default to `C:\\Program Files\\Unity\\Hub\\Editor` (Required to find Unity path)

`UNITYHUB` : default to `C:\Program Files\Unity Hub\Unity Hub.exe` (Required to install missing Unity version through Hub)

`JENKINS_BUILD_ARCHIVE` : Second backup location for all build results files. Includes .aab and symbol link file for later debug. (If not set, Errors will be ignore and build file only accessible on jenkins server)

## Helpful tips

Search these Jenkins server plugins: All Blue Ocean, Job DSL, Pipeline, PowerShell

Set Always scan with interval 1 minute because you dont have website server.

In jenkins server installation folder. Change `jenkins.xml` line to this.

`<arguments>-Xrs -Xss4m -Xmx1024m -Dhudson.lifecycle=hudson.lifecycle.WindowsServiceLifecycle -jar "%BASE%\jenkins.war" --httpListenAddress=127.0.0.1 --httpPort=8080 --webroot="%BASE%\war" --prefix="/jenkins"</arguments>`

https://stackoverflow.com/questions/39340322/how-to-reset-the-use-password-of-jenkins-on-windows

When create new multi-branch pipeline. Set Git setting to this.
![git](/doc/git-sample.jpg)