# Unity Jenkinsfile

Note: Currently this project is used for internal-team at my work place. There might some missing doc and setup not included and project is in development.

Although it is ready to run with any random project. Work for both building simple Android and fastlane build for iOS.
Just drag these files in and it will run on your Jenkins Server.


Multi-branch Jenkinsfile and python script for automated **Android** build Production: Install Unity -> Build Unity --> Push to internal Google Play -> Send Slack notification.

Made specifically for Windows Standalone Server. (Meaning no special install and setup for server. Just install jenkins setup some system variables and it will ready to go). With MacOSX, there are lots of special steps to setup fastlane, allow open ssh port with jenkins. You have to figure out on your own.

Read [pipeline doc](/JenkinsFiles/ci/README.md) for how to setup UnityProject builder script.

## Install
Simply copy this entire project to root .git folder. Jenkins only need to detect Jenkinsfile in root folder.

`git clone https://github.com/VAD37/unity-jenkinsfile.git`

## Setup Jenkins Server

Due to limitation of Docker and Unity Linux during this project was made. It was much easier to build Unity on Windows.

**IMPORANT** must install mingw64 as bash shell in Windows. If you dont know what is Mingw is, it is the same as Git Bash.

You can install mingw64 or git bash through Chocolatey for best result.

Windows Jenkins will not run git command with any other Linux shell like Window-Linux or cygwin due to Different in window directory path.


Install python on all build agents.

Go into jenkins settings/ Manage Nodes and set all agents with tags "Windows" so pipeline will run when finding agents. (remove agents option from Jenkinsfile if you dont want to use tags)

# Enviroment Variables Requirements

**IMPORANT** Make sure git Bash or mingw64 bash.exe be on top in `Path` environment. Other linux shell command can still be accessible when use in pipeline.
After reset environment. Restart server. (This was required due to conflict between '\' and '/' in old window-jenkins version)

![sapmple](/doc/env-path.jpg)

`JAVA_HOME` : Required for android build. Just install newest Java JDK

`UNITY_INSTALL_LOCATION` : default to `C:\\Program Files\\Unity\\Hub\\Editor` (Required to find Unity path)

`UNITYHUB` : default to `C:\Program Files\Unity Hub\Unity Hub.exe` (Required to install missing Unity version through Hub)

## Helpful tips

For setting up project password and pre-build function use `IPreprocessBuildWithReport`

```cs
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.Build.Reporting;
using UnityEditor.AddressableAssets.Settings;
using UnityEditor.Callbacks;
using UnityEngine;


public class BuildProcessor : IPreprocessBuildWithReport {
    
    [PostProcessBuild(1)]
    public static void DeleteDebugPrefabInResources(BuildTarget target, string pathToBuiltProject) {
        Debug.Log( pathToBuiltProject );        
    }

    public int callbackOrder { get; }
    public void OnPreprocessBuild(BuildReport report)
    {
        var pipeline = Builder.Configs["PIPELINE"];
        // 3 type of pipelien: production, develop, internal
        if(pipeline != "production") 
        {
            // Add develop prefab to resource or create readable file in resources
        }
        
        
        PlayerSettings.Android.useCustomKeystore = true;
        PlayerSettings.Android.keystoreName      = "Path to keystore file in project. The same one as in Editor";
        PlayerSettings.Android.keyaliasName      = "";
        PlayerSettings.Android.keyaliasPass      = "";
        PlayerSettings.Android.keystorePass      = "";
        PlayerSettings.Android.minSdkVersion     = AndroidSdkVersions.AndroidApiLevel19; // minium API for override adb install to work with        
        AssetDatabase.SaveAssets();
		
		AddressableAssetSettings.BuildPlayerContent();
    }
}
```


Search these Jenkins server plugins: All Blue Ocean, Job DSL, Pipeline, PowerShell

Set Always scan with interval 1 minute.

In jenkins server installation folder. Change `jenkins.xml` line to this. (extra file size limit)

`<arguments>-Xrs -Xss4m -Xmx1024m -Dhudson.lifecycle=hudson.lifecycle.WindowsServiceLifecycle -jar "%BASE%\jenkins.war" --httpListenAddress=127.0.0.1 --httpPort=8080 --webroot="%BASE%\war" --prefix="/jenkins"</arguments>`

https://stackoverflow.com/questions/39340322/how-to-reset-the-use-password-of-jenkins-on-windows

When create new multi-branch pipeline. Set Git setting to this.
![git](/doc/git-sample.jpg)
