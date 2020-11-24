using UnityEditor;
using System.Linq;
using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEditor.Build.Reporting;
using UnityEditor.U2D;
using UnityEngine;
using UnityEditor.AddressableAssets.Settings;

public static class Builder
{
    private const string RootTools = "Tools/JenkinsPipeline/";

    #region Build

    public static void Build()
    {
        BeforeBuild();
        string pipeline = Configs["PIPELINE"];
        // This was set during CI pipeline
        Console.WriteLine($"LOG::: Build Target {EditorUserBuildSettings.activeBuildTarget}");
        switch (EditorUserBuildSettings.activeBuildTarget)
        {
            case BuildTarget.iOS:
                BuildiOS();
                break;
            case BuildTarget.Android:
                BuildAndroid();
                break;
            default: throw new Exception("Not support this build target " + EditorUserBuildSettings.activeBuildTarget);
        }

        void BuildAndroid()
        {
            Console.WriteLine($"LOG::: Start building android {pipeline}");
            switch (pipeline)
            {
                case "production":
                    BuildAndroidProduction();
                    break;
                default:
                    BuildAndroidDevelopment();
                    break;
            }
        }

        void BuildiOS()
        {
            Console.WriteLine($"LOG::: Start building iOS {pipeline}");
            switch (pipeline)
            {
                case "production":
                    BuildXcodeProject();
                    break;
                default:
                    BuildXcodeProjectDevelopment();
                    break;
            }
        }
    }

    public static void BuildAndroidProduction()
    {
        AddScriptingDefineSymbol("PRODUCTION");
        RemoveScriptingDefineSymbol("DEVELOPMENT"); // Someone might accidentally add this
        EditorUserBuildSettings.development = false;
        EditorUserBuildSettings.allowDebugging = false;
        EditorUserBuildSettings.symlinkLibraries = true;
        EditorUserBuildSettings.androidCreateSymbolsZip = true;
        EditorUserBuildSettings.buildAppBundle = true;
        EditorUserBuildSettings.exportAsGoogleAndroidProject = false;
        SwitchScriptingImplement(ScriptingImplementation.IL2CPP);

        BuildReport report = BuildPipeline.BuildPlayer(
            GetEnabledScenes(), GetAndroidBuildPath(".aab"), BuildTarget.Android, BuildOptions.None);
        int code = (report.summary.result == BuildResult.Succeeded) ? 0 : 1;
        EditorApplication.Exit(code);
    }

    public static void BuildAndroidDevelopment()
    {
        PlayerSettings.Android.minSdkVersion =
            AndroidSdkVersions
                .AndroidApiLevel23; // APi 21 support downgrade adb. use api 23 as most popular test android
        AddScriptingDefineSymbol("DEVELOPMENT");
        EditorUserBuildSettings.development = false;
        EditorUserBuildSettings.allowDebugging = false;
        EditorUserBuildSettings.symlinkLibraries = false;
        EditorUserBuildSettings.androidCreateSymbolsZip = false;
        EditorUserBuildSettings.buildAppBundle = false;
        EditorUserBuildSettings.exportAsGoogleAndroidProject = false;
        SwitchScriptingImplement(ScriptingImplementation.IL2CPP);
        BuildReport report =
            BuildPipeline.BuildPlayer(GetEnabledScenes(), GetAndroidBuildPath(), BuildTarget.Android, BuildOptions.None);
        int code = (report.summary.result == BuildResult.Succeeded) ? 0 : 1;
        EditorApplication.Exit(code);
    }

    public static void BuildXcodeProject()
    {
        AddScriptingDefineSymbol("PRODUCTION");
        RemoveScriptingDefineSymbol("DEVELOPMENT"); // Someone might accidentally add this
        EditorUserBuildSettings.development = false;
        EditorUserBuildSettings.allowDebugging = false;
        EditorUserBuildSettings.symlinkLibraries = true;
        SwitchScriptingImplement(ScriptingImplementation.IL2CPP);
        BuildReport report =
            BuildPipeline.BuildPlayer(GetEnabledScenes(), GetXcodeFolder(), BuildTarget.iOS, BuildOptions.None);
        int code = (report.summary.result == BuildResult.Succeeded) ? 0 : 1;
        EditorApplication.Exit(code);
    }

    public static void BuildXcodeProjectDevelopment()
    {
        AddScriptingDefineSymbol("DEVELOPMENT");
        EditorUserBuildSettings.development = false;
        EditorUserBuildSettings.allowDebugging = false;
        EditorUserBuildSettings.symlinkLibraries = false;
        SwitchScriptingImplement(ScriptingImplementation.IL2CPP);
        BuildReport report =
            BuildPipeline.BuildPlayer(GetEnabledScenes(), GetXcodeFolder(), BuildTarget.iOS, BuildOptions.None);
        int code = (report.summary.result == BuildResult.Succeeded) ? 0 : 1;
        EditorApplication.Exit(code);
    }

    private static void SwitchScriptingImplement(ScriptingImplementation target)
    {
        if (PlayerSettings.GetScriptingBackend(BuildTargetGroup.Android) != target)
            PlayerSettings.SetScriptingBackend(BuildTargetGroup.Android, target);
    }

    public static void AddScriptingDefineSymbol(params string[] defines)
    {
        string definesString =
            PlayerSettings.GetScriptingDefineSymbolsForGroup(EditorUserBuildSettings.selectedBuildTargetGroup);
        var allDefines = definesString.Split(';').ToList();
        allDefines.AddRange(defines);
        PlayerSettings.SetScriptingDefineSymbolsForGroup(EditorUserBuildSettings.selectedBuildTargetGroup, string.Join(";", allDefines.ToArray()));
    }

    public static void RemoveScriptingDefineSymbol(params string[] defines)
    {
        string definesString =
            PlayerSettings.GetScriptingDefineSymbolsForGroup(EditorUserBuildSettings.selectedBuildTargetGroup);
        var allDefines = definesString.Split(';').ToList();
        foreach (string define in defines)
        {
            if (allDefines.Contains(define))
            {
                Debug.Log($"LOG::: remove {define} from Define Symbols");
                allDefines.Remove(define);
            }
        }

        PlayerSettings.SetScriptingDefineSymbolsForGroup(EditorUserBuildSettings.selectedBuildTargetGroup,
            string.Join(";", allDefines.ToArray()));
    }

    #endregion

    #region Environment

    private static void BeforeBuild()
    {
        SpriteAtlasUtility.PackAllAtlases(EditorUserBuildSettings.activeBuildTarget, false);

        AssetDatabase.SaveAssets();

        PrintAllEnviromentVariables();
        WriteBuildInfoFile();

        SetupBuildVersion();
        SetupBuildBundleVersion();

        AssetDatabase.SaveAssets();
        BuildAddressable();
    }

    private static void BuildAddressable()
    {
        AddressableAssetSettings.CleanPlayerContent(); // Clean everything
        Console.WriteLine("LOG::: Start Build addressable");
        
        // There is issue where Addressable in batch mode. Ask for confirm scene modified and stop build.
        // You can check log and see that addressable build time = 0
        AssetDatabase.SaveAssets();
        AddressableAssetSettings.BuildPlayerContent();
        Console.WriteLine("LOG::: Build addressable Done");
    }

    private static void SetupBuildBundleVersion()
    {
        try
        {
            string buildNumber = GetEnvironmentVariable("BUILD_NUMBER");
            int buildCount = int.Parse(buildNumber);
            if (Configs.ContainsKey("BUILD_BASE_BUNDLE_VERSION"))
            {
                int baseBuildCount = int.Parse(Configs["BUILD_BASE_BUNDLE_VERSION"]);
                PlayerSettings.Android.bundleVersionCode = baseBuildCount + buildCount;
                PlayerSettings.iOS.buildNumber = (baseBuildCount + buildCount).ToString();
            }
            else
            {
                PlayerSettings.Android.bundleVersionCode = buildCount;
                PlayerSettings.iOS.buildNumber = (buildCount).ToString();
            }
        }
        catch (Exception e)
        {
            Console.WriteLine("ERROR::: MISSING Environment for Build versioning");
            Console.WriteLine(e);
        }
    }

    private static void SetupBuildVersion()
    {
        // Change the game version and bundle version if config have it
        if (Configs.ContainsKey("RELEASE_VERSION"))
        {
            // version set up by semantic versioning
            Console.WriteLine("LOG::: Found release version in config");
            PlayerSettings.bundleVersion = Configs["RELEASE_VERSION"];
        }
        else
        {
            AppendConfig("RELEASE_VERSION", PlayerSettings.bundleVersion);
        }
    }

    private static string GetEnvironmentVariable(string name)
    {
        var envs = Environment.GetEnvironmentVariables();
        foreach (DictionaryEntry entry in envs)
            if (name == entry.Key.ToString())
                return entry.Value.ToString();
        return null;
    }

    private static void PrintAllEnviromentVariables()
    {
        Console.WriteLine("----------START ENVIRONMENT VARIABLES---------");
        var envs = Environment.GetEnvironmentVariables();
        foreach (DictionaryEntry entry in envs)
            Console.WriteLine(entry.Key + " " + entry.Value);

        var args = Environment.GetCommandLineArgs();
        int length = args.Length;
        for (var i = 0; i < length; i++)
            if (args[i].Contains("-") && i + 1 != length)
                Console.WriteLine(args[i] + " " + args[++i]);
        Console.WriteLine("----------END ENVIRONMENT VARIABLES---------");
    }

    // This is build information. Show this in game to identify build version
    private static void WriteBuildInfoFile()
    {
        AppendConfig("BUNDLE_VERSION", PlayerSettings.bundleVersion);
        var path = "Assets/Resources/BuildInfo.txt";
        string branch = Configs["GIT_BRANCH"];
        string commiter = Configs["GIT_COMMITER_NAME"];
        string hash = Configs["GIT_COMMIT_SHORT_HASH"];
        string buildNumber = GetEnvironmentVariable("BUILD_NUMBER");
        string time = Configs["GIT_COMMIT_DATE"];
        DateTime.TryParse(time, out var commitDate);
        string buildName =
            $"[{branch}][{commiter}] version:{PlayerSettings.bundleVersion} build:{buildNumber} time:{time} hash:{hash} unity:{Application.unityVersion}";
        string versionText = $"Version: {PlayerSettings.bundleVersion}.{buildNumber}.{commitDate:s}";
        Directory.CreateDirectory("Assets/Resources");
        var writer = new StreamWriter(path, false);
        writer.WriteLine(buildName);
        writer.WriteLine(versionText);
        writer.Close();
    }

    #endregion

    #region Naming build folder

    private static string[] GetEnabledScenes()
    {
        return (from scene in EditorBuildSettings.scenes where scene.enabled select scene.path).ToArray();
    }

    // File name is simple. Only when archive/moving file. It change name using shell
    public static string GetAndroidBuildPath(string extension = ".apk")
    {
        var projectDir = new DirectoryInfo(Application.dataPath).Parent;
        var time = DateTime.Now; // Use build time as name not git Commit date time. Due to sometime parse failed
        string branch = Configs["GIT_BRANCH"];
        branch = ReplaceInvalidChars(branch);
        string buildName = $"{PlayerSettings.productName.Replace(" ", "")}--{time:yyyy-MM-dd--HH-mm}--{branch}";
        buildName = $"{buildName}" + extension;
        string path = Path.Combine(projectDir.FullName, "build", "Android", buildName);
        Console.WriteLine("BUILD PATH: " + path);
        return path;
    }

    public static string ReplaceInvalidChars(string filename)
    {
        return string.Join("_", filename.Split(Path.GetInvalidFileNameChars()));
    }

    public static string GetXcodeFolder()
    {
        var projectDir = new DirectoryInfo(Application.dataPath).Parent;
        string path = Path.Combine(projectDir.FullName, "build","iOS");
        Debug.Log(path);
        Console.WriteLine("BUILD PATH: " + path);
        return path;
    }

    #endregion

    #region Configs

    private static Dictionary<string, string> _configs;

    public static Dictionary<string, string> Configs
    {
        get
        {
            if (_configs != null)
                return _configs;
            InitConfig();
            return _configs;
        }
    }

    private static void InitConfig()
    {
        var projectDir = new DirectoryInfo(Application.dataPath).Parent;
        string configFile = Path.Combine(projectDir.FullName, "config.cfg");
        var lines = File.ReadAllLines(configFile);
        _configs = new Dictionary<string, string>();
        try
        {
            foreach (string line in lines)
            {
                var splits = line.Split('=');
                string key = splits[0];
                string value = splits.Length > 1 ? splits[1] : null;
                _configs.Add(key, value?.Replace("\"", ""));
            }
        }
        catch (Exception e)
        {
            Console.WriteLine("ERROR::: Broken config files");
            Console.WriteLine(e);
        }
    }

    private static void AppendConfig(string key, string value)
    {
        var projectDir = new DirectoryInfo(Application.dataPath).Parent;
        string configFile = Path.Combine(projectDir.FullName, "config.cfg");
        try
        {
            File.AppendAllLines(configFile, new[] {$"{key}={value}"});
        }
        catch (Exception e)
        {
            Console.WriteLine("ERROR::: Broken config files");
            Console.WriteLine(e);
        }
    }
    #endregion
}