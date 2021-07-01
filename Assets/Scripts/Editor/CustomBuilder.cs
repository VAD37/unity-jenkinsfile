using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using Game;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEditor.U2D;
using UnityEngine;

public static class CustomBuilder
{
    private const string RootTools = "Tools/JenkinsPipeline/";
    private const string UserKeystore = "user.keystore";
    private const string KeyaliasName = "";
    private const string KeyaliasPass = "";
    private const string KeystorePass = "";


    #region Build

    public static void Build()
    {
        BeforeBuild();
        var pipeline = Configs["PIPELINE"];
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

        AfterBuild();
    }

    private static void AfterBuild()
    {
        // var report = BuildReportTool.ReportGenerator.CreateReport();
        // var reportExportFile = GetAndroidBuildPath(".buildreport");
        // System.IO.File.Copy(report, reportExportFile, true);
    }

    public static void BuildAndroidProduction()
    {
        AddScriptingDefineSymbol("PRODUCTION");
        RemoveScriptingDefineSymbol("DEVELOPMENT"); // Someone might accidentally add this
        EditorUserBuildSettings.development = false;
        EditorUserBuildSettings.allowDebugging = false;
        EditorUserBuildSettings.symlinkLibraries = false;
        EditorUserBuildSettings.androidCreateSymbolsZip = false;
        EditorUserBuildSettings.buildAppBundle = true;
        EditorUserBuildSettings.exportAsGoogleAndroidProject = false;
        SwitchScriptingImplement(ScriptingImplementation.IL2CPP);

        var report = BuildPipeline.BuildPlayer(
            GetEnabledScenes(), GetAndroidBuildPath(".aab"), BuildTarget.Android, BuildOptions.None);
        var code = report.summary.result == BuildResult.Succeeded ? 0 : 1;
        EditorApplication.Exit(code);
    }

    public static void BuildAndroidDevelopment()
    {
        PlayerSettings.Android.useCustomKeystore = false;

        AddScriptingDefineSymbol("DEVELOPMENT");
        EditorUserBuildSettings.development = false;
        EditorUserBuildSettings.allowDebugging = false;
        EditorUserBuildSettings.symlinkLibraries = false;
        EditorUserBuildSettings.androidCreateSymbolsZip = false;
        EditorUserBuildSettings.buildAppBundle = false;
        EditorUserBuildSettings.exportAsGoogleAndroidProject = false;
        SwitchScriptingImplement(ScriptingImplementation.IL2CPP);
        var buildPlayerOptions = new BuildPlayerOptions();
        buildPlayerOptions.scenes = GetEnabledScenes();
        buildPlayerOptions.target = BuildTarget.Android;
        buildPlayerOptions.locationPathName = GetAndroidBuildPath();

        // var report = BuildPipeline.BuildPlayer(GetEnabledScenes(), GetAndroidBuildPath(), BuildTarget.Android, BuildOptions.None);
        var report = BuildPipeline.BuildPlayer(buildPlayerOptions);
        var code = report.summary.result == BuildResult.Succeeded ? 0 : 1;
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
        var report = BuildPipeline.BuildPlayer(GetEnabledScenes(), GetXcodeFolder(), BuildTarget.iOS, BuildOptions.None);
        var code = report.summary.result == BuildResult.Succeeded ? 0 : 1;
        EditorApplication.Exit(code);
    }

    public static void BuildXcodeProjectDevelopment()
    {
        AddScriptingDefineSymbol("DEVELOPMENT");
        EditorUserBuildSettings.development = false;
        EditorUserBuildSettings.allowDebugging = false;
        EditorUserBuildSettings.symlinkLibraries = false;
        SwitchScriptingImplement(ScriptingImplementation.IL2CPP);
        var report =
            BuildPipeline.BuildPlayer(GetEnabledScenes(), GetXcodeFolder(), BuildTarget.iOS, BuildOptions.None);
        var code = report.summary.result == BuildResult.Succeeded ? 0 : 1;
        EditorApplication.Exit(code);
    }

    private static void SwitchScriptingImplement(ScriptingImplementation target)
    {
        if (PlayerSettings.GetScriptingBackend(BuildTargetGroup.Android) != target)
            PlayerSettings.SetScriptingBackend(BuildTargetGroup.Android, target);
    }

    public static void AddScriptingDefineSymbol(params string[] defines)
    {
        var definesString =
            PlayerSettings.GetScriptingDefineSymbolsForGroup(EditorUserBuildSettings.selectedBuildTargetGroup);
        var allDefines = definesString.Split(';').ToList();
        allDefines.AddRange(defines);
        PlayerSettings.SetScriptingDefineSymbolsForGroup(EditorUserBuildSettings.selectedBuildTargetGroup,
            string.Join(";", allDefines.ToArray()));
    }

    public static void RemoveScriptingDefineSymbol(params string[] defines)
    {
        var definesString =
            PlayerSettings.GetScriptingDefineSymbolsForGroup(EditorUserBuildSettings.selectedBuildTargetGroup);
        var allDefines = definesString.Split(';').ToList();
        foreach (var define in defines)
            if (allDefines.Contains(define))
            {
                Debug.Log($"LOG::: remove {define} from Define Symbols");
                allDefines.Remove(define);
            }

        PlayerSettings.SetScriptingDefineSymbolsForGroup(EditorUserBuildSettings.selectedBuildTargetGroup,
            string.Join(";", allDefines.ToArray()));
    }

    #endregion

    #region Environment

    public static void CleanUpDeletedScenes()
    {
        var currentScenes = EditorBuildSettings.scenes;
        EditorBuildSettings.scenes = currentScenes.Where(ebss => AssetDatabase.LoadAssetAtPath(ebss.path, typeof(SceneAsset)) != null).ToArray();
    }

    private static void BeforeBuild()
    {
        CleanUpDeletedScenes();

        KeyStore();

        SpriteAtlasUtility.PackAllAtlases(EditorUserBuildSettings.activeBuildTarget, false);

        AssetDatabase.SaveAssets();

        PrintAllEnviromentVariables();
        WriteBuildInfoFile();

        SetupBuildVersion();
        SetupBuildBundleVersion();

        AssetDatabase.SaveAssets();
        BuildAddressable();
    }

    private static void KeyStore()
    {
        // PlayerSettings.Android.useCustomKeystore = false;
        PlayerSettings.Android.useCustomKeystore = true;
        PlayerSettings.Android.keystoreName = UserKeystore;
        PlayerSettings.Android.keyaliasName = KeyaliasName;
        PlayerSettings.Android.keyaliasPass = KeyaliasPass;
        PlayerSettings.Android.keystorePass = KeystorePass;
    }

    private static void BuildAddressable()
    {
        // AddressableAssetSettings.CleanPlayerContent(); // Clean everything
        // Console.WriteLine("LOG::: Start Build addressable");
        //
        // // There is issue where Addressable in batch mode. Ask for confirm scene modified and stop build.
        // // You can check log and see that addressable build time = 0
        // AssetDatabase.SaveAssets();
        // AddressableAssetSettings.BuildPlayerContent();
        // Console.WriteLine("LOG::: Build addressable Done");
    }

    private static void SetupBuildBundleVersion()
    {
        try
        {
            var buildNumber = GetEnvironmentVariable("BUILD_NUMBER");
            var buildCount = int.Parse(buildNumber);
            if (Configs.ContainsKey("BUILD_BASE_BUNDLE_VERSION"))
            {
                var baseBuildCount = int.Parse(Configs["BUILD_BASE_BUNDLE_VERSION"]);
                PlayerSettings.Android.bundleVersionCode = baseBuildCount + buildCount;
                PlayerSettings.iOS.buildNumber = (baseBuildCount + buildCount).ToString();
            }
            else
            {
                PlayerSettings.Android.bundleVersionCode = buildCount;
                PlayerSettings.iOS.buildNumber = buildCount.ToString();
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
        var length = args.Length;
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
        var branch = Configs["GIT_BRANCH"];
        var commiter = Configs["GIT_COMMITER_NAME"];
        var hash = Configs["GIT_COMMIT_SHORT_HASH"];
        var buildNumber = GetEnvironmentVariable("BUILD_NUMBER");
        var time = Configs["GIT_COMMIT_DATE"];
        DateTime.TryParse(time, out var commitDate);
        var buildName =
            $"[{branch}][{commiter}] version:{PlayerSettings.bundleVersion} build:{buildNumber} time:{time} hash:{hash} unity:{Application.unityVersion}";
        var versionText = $"Version: {PlayerSettings.bundleVersion}.{buildNumber}.{commitDate:s}";
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
        var branch = Configs["GIT_BRANCH"];
        branch = ReplaceInvalidChars(branch);
        var buildName = $"{PlayerSettings.productName.Replace(" ", "")}--{time:yyyy-MM-dd--HH-mm}--{branch}";
        buildName = $"{buildName}" + extension;
        var path = Path.Combine(projectDir.FullName, "build", "Android", buildName);
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
        var path = Path.Combine(projectDir.FullName, "build", "iOS");
        Debug.Log(path);
        Console.WriteLine("BUILD PATH: " + path);
        return path;
    }

    #endregion

    #region Configs

    private static Dictionary<string, string> _configs;

    public static Dictionary<string, string> Configs {
        get {
            if (_configs != null)
                return _configs;
            InitConfig();
            return _configs;
        }
    }

    private static void InitConfig()
    {
        var projectDir = new DirectoryInfo(Application.dataPath).Parent;
        var configFile = Path.Combine(projectDir.FullName, "config.cfg");
        var lines = File.ReadAllLines(configFile);
        _configs = new Dictionary<string, string>();
        try
        {
            foreach (var line in lines)
            {
                var splits = line.Split('=');
                var key = splits[0];
                var value = splits.Length > 1 ? splits[1] : null;
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
        var configFile = Path.Combine(projectDir.FullName, "config.cfg");
        try
        {
            File.AppendAllLines(configFile, new[] { $"{key}={value}" });
        }
        catch (Exception e)
        {
            Console.WriteLine("ERROR::: Broken config files");
            Console.WriteLine(e);
        }
    }

    #endregion
}
