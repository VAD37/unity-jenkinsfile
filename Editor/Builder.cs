﻿using UnityEditor;
using System.Linq;
using System;
using System.Collections;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Reflection;
using System.Text;
using UnityEngine;

public static class Builder
{
    private const string RootTools = "Tools/JenkinsPipeline/";
    
    public static void BuildInternal()
    {
        BeforeBuild();

        EditorUserBuildSettings.development    = true;
        EditorUserBuildSettings.allowDebugging = true;
        EditorUserBuildSettings.buildAppBundle = false;
        SwitchScriptingImplement(ScriptingImplementation.Mono2x);
        BuildPipeline.BuildPlayer(
            GetEnabledScenes(),
            GetFileName(),
            BuildTarget.Android,
            BuildOptions.Development | BuildOptions.AllowDebugging
        );
    }

    public static void BuildProduction()
    {
        BeforeBuild();
        
        EditorUserBuildSettings.development             = false;
        EditorUserBuildSettings.allowDebugging          = false;
        EditorUserBuildSettings.symlinkLibraries        = true;
        EditorUserBuildSettings.androidCreateSymbolsZip = true;
        EditorUserBuildSettings.buildAppBundle = true;
        SwitchScriptingImplement(ScriptingImplementation.IL2CPP);
        
        BuildPipeline.BuildPlayer(
            GetEnabledScenes(),
            GetFileName(".aab"),
            BuildTarget.Android,
            BuildOptions.None 
        );
    }

    private static void SwitchScriptingImplement(ScriptingImplementation target)
    {
        if (PlayerSettings.GetScriptingBackend(BuildTargetGroup.Android) != target)
            PlayerSettings.SetScriptingBackend(BuildTargetGroup.Android, target);
    }

    public static void BuildDevelopment()
    {
        BeforeBuild();

        EditorUserBuildSettings.development = true;
        EditorUserBuildSettings.allowDebugging = true;
        EditorUserBuildSettings.symlinkLibraries = false;
        EditorUserBuildSettings.androidCreateSymbolsZip = false;
        EditorUserBuildSettings.buildAppBundle = false;
        SwitchScriptingImplement(ScriptingImplementation.IL2CPP);
        BuildPipeline.BuildPlayer(
            GetEnabledScenes(),
            GetFileName(),
            BuildTarget.Android,
            BuildOptions.Development | BuildOptions.AllowDebugging
        );
    }
    
    public static void BuildExportProject()
    {
        BeforeBuild();
        
        EditorUserBuildSettings.development                  = false;
        EditorUserBuildSettings.allowDebugging               = false;
        EditorUserBuildSettings.symlinkLibraries             = true;
        EditorUserBuildSettings.androidCreateSymbolsZip      = true;
        EditorUserBuildSettings.buildAppBundle               = false;
        EditorUserBuildSettings.exportAsGoogleAndroidProject = true;
        SwitchScriptingImplement(ScriptingImplementation.IL2CPP);
        BuildPipeline.BuildPlayer(
            GetEnabledScenes(),
            GetFolderName(),
            BuildTarget.Android,
            BuildOptions.AcceptExternalModificationsToPlayer
        );
    }
    
    public static void BuildExportProjectDevelopment()
    {
        BeforeBuild();
        
        EditorUserBuildSettings.development                  = true;
        EditorUserBuildSettings.allowDebugging               = true;
        EditorUserBuildSettings.symlinkLibraries             = true;
        EditorUserBuildSettings.androidCreateSymbolsZip      = true;
        EditorUserBuildSettings.buildAppBundle               = false;
        EditorUserBuildSettings.exportAsGoogleAndroidProject = true;
        SwitchScriptingImplement(ScriptingImplementation.IL2CPP);
        BuildPipeline.BuildPlayer(
            GetEnabledScenes(),
            GetFolderName(),
            BuildTarget.Android,
            BuildOptions.AcceptExternalModificationsToPlayer | BuildOptions.Development
        );
    }

    [MenuItem(RootTools+"Show Current BuildPlayerOptions")]
    public static void PrintCurrentBuildSettings()
    {
        var defaultOptions = new BuildPlayerOptions();
        // Get static internal "GetBuildPlayerOptionsInternal" method
        MethodInfo method = typeof(BuildPlayerWindow.DefaultBuildMethods).GetMethod(
            "GetBuildPlayerOptionsInternal",
            BindingFlags.NonPublic | BindingFlags.Static);
        // invoke internal method
        var buildOptions = (BuildPlayerOptions) method.Invoke(null, new object[] {false, defaultOptions});
        Debug.Log(buildOptions.options);
    }
    
    private static void BeforeBuild()
    {
        PrintAllEnviromentVariables();
        // Change the game version and bundle version if config have it
        if (Configs.ContainsKey("RELEASE_VERSION")) {
            Console.WriteLine("LOG::: Found release version in config");
            PlayerSettings.bundleVersion = Configs["RELEASE_VERSION"];
            // var version = new Version(Configs["RELEASE_VERSION"]);
        }
        else
        {
            AddConfigToFile("RELEASE_VERSION", PlayerSettings.bundleVersion);
        }

        try
        {
            var buildNumber = GetArgument("BUILD_NUMBER");
            var buildCount = int.Parse(buildNumber);
            if(Configs.ContainsKey("BUILD_BASE_BUNDLE_VERSION")){       
                var baseBuildCount = int.Parse(Configs["BUILD_BASE_BUNDLE_VERSION"]);            
                PlayerSettings.Android.bundleVersionCode = baseBuildCount + buildCount;
            }
            else {
                PlayerSettings.Android.bundleVersionCode = buildCount;
            }
        }
        catch (System.Exception e)
        {
            Console.WriteLine("ERROR::: MISSING Enviroment files");
            Console.WriteLine(e);
        }
        var buildFolder =  Path.GetFullPath("build/");
        
        bool exists = System.IO.Directory.Exists(buildFolder);
        if(!exists)
            System.IO.Directory.CreateDirectory(buildFolder);

        WriteBuildInfoFile();
    }

    static string GetArgument(string name) {
        string[] args   = Environment.GetCommandLineArgs();
        var      length = args.Length;
        for (int i = 0; i < length; i++) {
            if (args[i].Contains(name) &&
                i != length - 1) { return args[i + 1]; }
        }
        return null;
    }

    static void PrintAllEnviromentVariables() {
        var envs = Environment.GetEnvironmentVariables();
        foreach (DictionaryEntry entry in envs) { Console.WriteLine(entry.Key + " " + entry.Value); }

        string[] args   = Environment.GetCommandLineArgs();
        var      length = args.Length;
        for (int i = 0; i < length; i++) {
            if (args[i].Contains("-") &&
                i + 1 != length)
                Console.WriteLine("ENV::: " + args[i] + " " + args[++i]);
        }
    }

    static string[] GetEnabledScenes() {
        return (from scene in EditorBuildSettings.scenes where scene.enabled select scene.path).ToArray();
    }

    public static string GetFileName(string extension = ".apk") {
        string buildName = PlayerSettings.productName;
        var projectDir = new DirectoryInfo(Application.dataPath).Parent;
        
        var    branch    = GetArgument("GIT_BRANCH");
        var    commiter  = GetArgument("GIT_COMMITER_NAME");
        var    id        = GetEnv("BUILD_ID");
        var    time      = GetArgument("GIT_COMMITER_DATE");

        string timeString = null;

        if (DateTimeOffset.TryParseExact(time, "ddd MMM d HH:mm:ss yyyy K", CultureInfo.InvariantCulture, DateTimeStyles.None,
                                         out var dto))
            timeString = dto.DateTime.ToString("s");
        if (DateTimeOffset.TryParseExact(time, "ddd, d MMM yyyy HH:mm:ss K", CultureInfo.InvariantCulture, DateTimeStyles.None,
                                         out var dto2))
            timeString = dto2.DateTime.ToString("s").Replace(":", "");
        if (string.IsNullOrEmpty(timeString))
            timeString = time;
        
        buildName = $"{timeString} {id}-{commiter}-{branch}-{buildName} {PlayerSettings.bundleVersion}" + extension;

        var path       = Path.Combine(projectDir.FullName, "build", buildName);

        Debug.Log(path);
        Console.WriteLine("BUILD PATH: " + path);
        return path;
    }
    
    public static string GetFolderName() {
        string buildName  = "export" ;
        var    projectDir = new DirectoryInfo(Application.dataPath).Parent;
        var    path       = Path.Combine(projectDir.FullName, "build", buildName);
        Debug.Log(path);
        Console.WriteLine("BUILD PATH: " + path);
        return path;
    }

    static string GetEnv(string key) {
        if (string.IsNullOrEmpty(key)) return "";
        try {
            var envVar = Environment.GetEnvironmentVariable(key);
            Console.WriteLine("Get environment variables " + key + " - " + envVar);
            return envVar;
        }
        catch {
            Console.WriteLine("Failed to get environment variables " + key);
        }
        return "";
    }

    private static Dictionary<string, string> _configs;
    public static Dictionary<string, string> Configs {
        get {
            if (_configs != null) return _configs;
            InitConfig();
            return _configs;
        }
    }

    static void InitConfig()
    {
        var projectDir = new DirectoryInfo(Application.dataPath).Parent;
        var configFile = Path.Combine(projectDir.FullName, "config.cfg");
        var lines = File.ReadAllLines(configFile);
        _configs = new Dictionary<string, string>();
        try {
            foreach (string line in lines) {
                var splits = line.Split('=');
                string key = splits[0];
                string value = splits.Length > 1 ? splits[1] : null;
                _configs.Add(key, value);
                Debug.Log("Found Config: " + key + " - " + value);
            }
        } catch (Exception e) {
            Console.WriteLine("ERROR::: Broken config files");
            Console.WriteLine(e);
        }
    }
    static void AddConfigToFile(string key, string value)
    {
        var projectDir = new DirectoryInfo(Application.dataPath).Parent;
        var configFile = Path.Combine(projectDir.FullName, "config.cfg");
        try {
            File.AppendAllLines(configFile, new []{$"{key}={value}"});
        } catch (Exception e) {
            Console.WriteLine("ERROR::: Broken config files");
            Console.WriteLine(e);
        }
    }
    
    private static void WriteBuildInfoFile() {
        string path = "Assets/Resources/BuildInfo.txt";
        var branch   = GetArgument("GIT_BRANCH");
        var commiter = GetArgument("GIT_COMMITER_NAME");
        var hash = GetArgument("GIT_COMMIT_SHORT_HASH");
        var buildNumber = GetEnv("BUILD_NUMBER");
        var time = GetArgument("GIT_COMMITER_DATE");
        var buildName = $"[{branch}][{commiter}] version:{PlayerSettings.bundleVersion} build:{buildNumber} time:{time} hash:{hash} unity:{Application.unityVersion}";
        
        Directory.CreateDirectory("Assets/Resources");
        var writer = new StreamWriter(path);
        writer.WriteLine(buildName);
        writer.Close();
    }
}