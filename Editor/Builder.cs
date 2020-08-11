using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using UnityEditor;
using UnityEditor.AddressableAssets.Settings;
using UnityEditor.Build.Reporting;
using UnityEditor.Callbacks;
using UnityEditor.U2D;
using UnityEngine;

/// <summary>
///     Design for jenkins pipeline will not run in normal/editor build batchmode.
/// </summary>
public static class Builder
{
    private const string RootTools = "Tools/JenkinsPipeline/";

    #region Build Methods

    /// <summary>
    /// This method was made specifically for batchmode and CI environments.
    /// Will not work with normal build in Editor.
    /// </summary>
    public static void Build()
    {
        BeforeBuild();
        // This was set during CI pipeline
        string pipeline = Configs["PIPELINE"];
        
        Console.WriteLine($"LOG::: Build Target {EditorUserBuildSettings.activeBuildTarget}");
        // Build target forced by batchmode command line
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
            // LOG::: format is the default UI log show in gitlab CI. This was migrated over.
            // Jenkins support color format
            Console.WriteLine($"LOG::: Start building android {pipeline}");
            switch (pipeline)
            {
                case "production":
                    BuildAndroidProduction();
                    break;
                case "development":
                    BuildAndroidDevelopment();
                    break;
                case "internal":
                    BuildAndroidDevelopment();
                    break;
                default: throw new Exception("Unknown pipeline type");
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
                case "development":
                    BuildXcodeProjectDevelopment();
                    break;
                case "internal":
                    BuildXcodeProjectDevelopment();
                    break;
                default: throw new Exception("Unknown pipeline type");
            }
        }
    }

    public static void BuildAndroidProduction()
    {
        AddScriptingDefineSymbol("PRODUCTION");
        EditorUserBuildSettings.development                  = false;
        EditorUserBuildSettings.allowDebugging               = false;
        EditorUserBuildSettings.symlinkLibraries             = true;
        EditorUserBuildSettings.androidCreateSymbolsZip      = true;
        EditorUserBuildSettings.buildAppBundle               = true;
        EditorUserBuildSettings.exportAsGoogleAndroidProject = false;
        SwitchScriptingImplement(ScriptingImplementation.IL2CPP);

        BuildReport report = BuildPipeline.BuildPlayer(GetEnabledScenes(), GetFileName(".aab"), BuildTarget.Android, BuildOptions.None);
        int code = (report.summary.result == BuildResult.Succeeded) ? 0 : 1;
        EditorApplication.Exit(code);
    }

    public static void BuildAndroidDevelopment()
    {
        AddScriptingDefineSymbol("DEVELOPMENT");
        EditorUserBuildSettings.development                  = false;
        EditorUserBuildSettings.allowDebugging               = false;
        EditorUserBuildSettings.symlinkLibraries             = false;
        EditorUserBuildSettings.androidCreateSymbolsZip      = false;
        EditorUserBuildSettings.buildAppBundle               = false;
        EditorUserBuildSettings.exportAsGoogleAndroidProject = false;
        SwitchScriptingImplement(ScriptingImplementation.IL2CPP);
        BuildReport report = BuildPipeline.BuildPlayer(GetEnabledScenes(), GetFileName(), BuildTarget.Android,BuildOptions.None);
        int code = (report.summary.result == BuildResult.Succeeded) ? 0 : 1;
        EditorApplication.Exit(code);
    }

    public static void BuildXcodeProject()
    {
        EditorUserBuildSettings.development      = false;
        EditorUserBuildSettings.allowDebugging   = false;
        EditorUserBuildSettings.symlinkLibraries = true;
        SwitchScriptingImplement(ScriptingImplementation.IL2CPP);
        BuildReport report = BuildPipeline.BuildPlayer(GetEnabledScenes(), GetXcodeFolder(), BuildTarget.iOS, BuildOptions.None);
        int         code   = (report.summary.result == BuildResult.Succeeded) ? 0 : 1;
        EditorApplication.Exit(code);
    }

    public static void BuildXcodeProjectDevelopment()
    {
        EditorUserBuildSettings.development      = true;
        EditorUserBuildSettings.allowDebugging   = true;
        EditorUserBuildSettings.symlinkLibraries = false;
        SwitchScriptingImplement(ScriptingImplementation.IL2CPP);
        BuildReport report = BuildPipeline.BuildPlayer(GetEnabledScenes(), GetXcodeFolder(), BuildTarget.iOS, BuildOptions.None);
        int         code   = (report.summary.result == BuildResult.Succeeded) ? 0 : 1;
        EditorApplication.Exit(code);
    }

    private static void SwitchScriptingImplement(ScriptingImplementation target)
    {
        if (PlayerSettings.GetScriptingBackend(BuildTargetGroup.Android) != target)
            PlayerSettings.SetScriptingBackend(BuildTargetGroup.Android, target);
    }

    public static void AddScriptingDefineSymbol(params string[] defines)
    {
        string definesString = PlayerSettings.GetScriptingDefineSymbolsForGroup(EditorUserBuildSettings.selectedBuildTargetGroup);
        var    allDefines    = definesString.Split(';').ToList();
        allDefines.AddRange(defines);
        PlayerSettings.SetScriptingDefineSymbolsForGroup(EditorUserBuildSettings.selectedBuildTargetGroup, string.Join(";", allDefines.ToArray()));
    }

    [MenuItem(RootTools + "Show Current BuildPlayerOptions")]
    public static void PrintCurrentBuildSettings()
    {
        var defaultOptions = new BuildPlayerOptions();
        // Get static internal "GetBuildPlayerOptionsInternal" method
        var method = typeof(BuildPlayerWindow.DefaultBuildMethods).GetMethod("GetBuildPlayerOptionsInternal", BindingFlags.NonPublic | BindingFlags.Static);
        // invoke internal method
        var buildOptions = (BuildPlayerOptions) method.Invoke(null, new object[] {false, defaultOptions});
        Debug.Log(buildOptions.options);
    }

    #endregion

    #region Environment

    private static void BeforeBuild()
    {
        // PrintAllEnviromentVariables();
        
        if (Configs.ContainsKey("PIPELINE"))
        {
            var pipeline = Configs["PIPELINE"];
            if(pipeline != "production")
            {
                string newPath = "Assets/Resources/DEVELOPMENT_REPORTER.prefab";
                var    asset   = AssetDatabase.GUIDToAssetPath(AssetDatabase.FindAssets("EDITOR_REPORTER")[0]);
                AssetDatabase.CopyAsset(asset, newPath);
            }
        }

        AndroidKey();

        // Rebuild Atlas u3d. Not old version sprite packer
        SpriteAtlasUtility.PackAllAtlases(EditorUserBuildSettings.activeBuildTarget,false);

        AssetDatabase.SaveAssets();
        
        
        WriteBuildInfoFile();

        SetupBuildVersion();
        SetupBuildBundleVersion();

        AssetDatabase.SaveAssets();
        BuildAddressable();
    }

    private static void AndroidKey()
    {
        var envs = Environment.GetEnvironmentVariables();
        if(envs.Contains("KEYSTORE_FILE") && envs.Contains("KEYSTORE_PASSWORD") && envs.Contains("KEYSTORE_ALIAS") && envs.Contains("KEYSTORE_ALIAS_PASSWORD")) {
            PlayerSettings.Android.useCustomKeystore = true;
            PlayerSettings.Android.keystoreName      = envs["KEYSTORE_FILE"].ToString();
            PlayerSettings.Android.keystorePass = envs["KEYSTORE_PASSWORD"].ToString();
            PlayerSettings.Android.keyaliasName      = envs["KEYSTORE_ALIAS"].ToString();
            PlayerSettings.Android.keyaliasPass      = envs["KEYSTORE_ALIAS_PASSWORD"].ToString();
        }
    }

    private static void BuildAddressable()
    {
        AddressableAssetSettings.CleanPlayerContent();
        Console.WriteLine("LOG::: Start Build addressable");
        AddressableAssetSettings.BuildPlayerContent(); // Sometime addressable have script errors cause CI stuck
        Console.WriteLine("LOG::: Build addressable Done");
    }

    private static void SetupBuildBundleVersion()
    {
        try
        {
            string buildNumber = GetEnvironmentVariable("BUILD_NUMBER");
            int    buildCount  = int.Parse(buildNumber);
            if (Configs.ContainsKey("BUILD_BASE_BUNDLE_VERSION"))
            {
                int baseBuildCount = int.Parse(Configs["BUILD_BASE_BUNDLE_VERSION"]);
                PlayerSettings.Android.bundleVersionCode = baseBuildCount + buildCount;
                PlayerSettings.iOS.buildNumber           = (baseBuildCount + buildCount).ToString();
            }
            else
            {
                PlayerSettings.Android.bundleVersionCode = buildCount;
                PlayerSettings.iOS.buildNumber           = (buildCount).ToString();
            }
        }
        catch (Exception e)
        {
            Console.WriteLine("ERROR::: MISSING Environment for Build versioning");
            Console.WriteLine(e);
        }
    }

    private static void SetupBuildVersion()
    { // Change the game version and bundle version if config have it
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

    // For testing purpose. All Secret and hidden password in env will be show in text.
    // Build have access to build log will see all passwords
    private static void PrintAllEnviromentVariables()
    {
        Console.WriteLine("----------START ENVIRONMENT VARIABLES---------");
        var envs = Environment.GetEnvironmentVariables();
        foreach (DictionaryEntry entry in envs)
            Console.WriteLine(entry.Key + " " + entry.Value);

        var args   = Environment.GetCommandLineArgs();
        int length = args.Length;
        for (var i = 0; i < length; i++)
            if (args[i].Contains("-") && i + 1 != length)
                Console.WriteLine(args[i] + " " + args[++i]);
        Console.WriteLine("----------END ENVIRONMENT VARIABLES---------");
    }

    // This is build information. Show this in game to identify build version
    /*
#if DEVELOPMENT_BUILD || DEVELOPMENT || UNITY_EDITOR

        private string _developmentDisplayText;

        void Start() 
        {
            _developmentDisplayText = Resources.Load<TextAsset>("BuildInfo").text;
        }
        
        private void OnGUI()
        {
            var style = GUI.skin.label;
            style.fontSize = 14;
            GUI.Label(new Rect(50, Screen.height - 20, Screen.width, 20), _developmentDisplayText, style);
        }
#endif
     */
    private static void WriteBuildInfoFile()
    {
        var    path        = "Assets/Resources/BuildInfo.txt";
        string branch      = Configs["GIT_BRANCH"];
        string commiter    = Configs["GIT_COMMITER_NAME"];
        string hash        = Configs["GIT_COMMIT_SHORT_HASH"];
        string buildNumber = GetEnvironmentVariable("BUILD_NUMBER");
        string time        = Configs["GIT_COMMIT_DATE"];
        string buildName =
            $"[{branch}][{commiter}] version:{PlayerSettings.bundleVersion} build:{buildNumber} time:{time} hash:{hash} unity:{Application.unityVersion}";

        Directory.CreateDirectory("Assets/Resources");
        var writer = new StreamWriter(path);
        writer.WriteLine(buildName);
        writer.Close();
    }

    #endregion

    #region Naming build folder

    private static string[] GetEnabledScenes()
    {
        return (from scene in EditorBuildSettings.scenes where scene.enabled select scene.path).ToArray();
    }

    // Use simple file name for quick install with adb. Only when archive/moving file change name sortable through CI.
    public static string GetFileName(string extension = ".apk")
    {
        MakeSureFolderExist(Path.Combine("build","Android"));
        string buildName  = PlayerSettings.productName;
        var    projectDir = new DirectoryInfo(Application.dataPath).Parent;
        buildName = $"{buildName}" + extension;
        string path = Path.Combine(projectDir.FullName, "build", "Android", buildName);
        Console.WriteLine("BUILD PATH: " + path);
        return path;
    }

    public static string GetXcodeFolder()
    {
        MakeSureFolderExist(Path.Combine("build", "iOS"));
        var    buildName  = "iOS";
        var    projectDir = new DirectoryInfo(Application.dataPath).Parent;
        string path       = Path.Combine(projectDir.FullName, "build", buildName);
        Console.WriteLine("BUILD PATH: " + path);
        return path;
    }

    // Jenkins need empty folder to work in shell. Sometime no files was build and it throw errors in shell
    private static void MakeSureFolderExist(string folderName)
    {
        string buildFolder = Path.GetFullPath(folderName);
        bool   exists      = Directory.Exists(buildFolder);
        if (!exists)
        {
            Console.WriteLine("LOG::: Create empty folder " + folderName);
            Directory.CreateDirectory(buildFolder);
        }
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
        var    projectDir = new DirectoryInfo(Application.dataPath).Parent;
        string configFile = Path.Combine(projectDir.FullName, "config.cfg");
        var    lines      = File.ReadAllLines(configFile);
        _configs = new Dictionary<string, string>();
        try
        {
            foreach (string line in lines)
            {
                var    splits = line.Split('=');
                string key    = splits[0];
                string value  = splits.Length > 1 ? splits[1] : null;
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
        var    projectDir = new DirectoryInfo(Application.dataPath).Parent;
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
    
    [PostProcessBuild(1)]
    public static void DeleteDebugPrefabInResources(BuildTarget target, string pathToBuiltProject) {
        Debug.Log( pathToBuiltProject );
        AssetDatabase.DeleteAsset("Assets/Resources/DEVELOPMENT_REPORTER.prefab");
    }
}