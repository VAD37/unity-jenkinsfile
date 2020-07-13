using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;

public static class JenkinsPipelineEditor
{
    private const string PackageName= "com.vad37.unity-jenkinsfile";
    private const string RootTools = "Tools/JenkinsPipeline/";
    
    [MenuItem(RootTools + "Install Pipeline (copy Jenkinsfile from package)")]
    private static void CopyPipelineScripts()
    {
        var projectDir = new DirectoryInfo(Application.dataPath).Parent;
        var packageDir =  new DirectoryInfo( Path.GetFullPath("Library/PackageCache/")).GetDirectories().First(x=>x.Name.Contains(PackageName));
        var copyPath = Path.Combine(packageDir.FullName, "JenkinsFiles");
        var desPath = projectDir.FullName;
        Debug.Log($"Copy files from: {copyPath} to {desPath}");
        //Now Create all of the directories
        foreach (string dirPath in Directory.GetDirectories(copyPath, "*", SearchOption.AllDirectories))
            Directory.CreateDirectory(dirPath.Replace(copyPath, desPath));

        //Copy all the files & Replaces any files with the same name
        foreach (string newPath in Directory.GetFiles(copyPath, "*.*", SearchOption.AllDirectories))
            if(!newPath.EndsWith(".meta"))
                File.Copy(newPath, newPath.Replace(copyPath, desPath), true);

        EditJenkinsFileVariable();
    }

    private static void EditJenkinsFileVariable()
    {
        var projectDir = new DirectoryInfo(Application.dataPath).Parent;
        var jenkinsfilePath = Path.Combine(projectDir.FullName, "Jenkinsfile");
        var gitRoot = GetProjectGitRoot();

        string jenkinsPath = File.ReadAllText(jenkinsfilePath);
        string truePath;
        if (gitRoot != null) {
            truePath = projectDir.FullName.Replace(gitRoot.FullName, "").TrimStart('\\', '/');
            if (string.IsNullOrEmpty(truePath)) truePath = " ";
        }
        else
            truePath = " ";
        
        string contents = jenkinsPath.Replace("[PROJECTPATH]",truePath);
        File.WriteAllText(jenkinsfilePath, contents);
    }

    // find .git folder
    private static DirectoryInfo GetProjectGitRoot()
    {
        var projectDir = new DirectoryInfo(Application.dataPath);
        while (true) {
            projectDir = projectDir.Parent;
            if (projectDir != null) {
                if (Directory.Exists(Path.Combine(projectDir.FullName, ".git"))) 
                    return projectDir;
            }
            else
                break;
        }
        return null;
    }

    [MenuItem(RootTools+"Force Update Package")]
    private static void RemoveLockFileFromManifest() {
        
        var dir  = Path.GetFullPath("Packages/manifest.json");;
        var text = File.ReadAllText(dir);


        var startLock         = text.IndexOf($"\"lock\"",          StringComparison.Ordinal);
        var startPackageName  = text.IndexOf($"\"{PackageName}\"", startLock,        StringComparison.Ordinal);
        var endPackageBracket = text.IndexOf("}",                  startPackageName, StringComparison.Ordinal);

        text = text.Remove(startPackageName, endPackageBracket - startPackageName + 1);
        File.WriteAllText(dir, text);
        
        AssetDatabase.Refresh();
    }
}