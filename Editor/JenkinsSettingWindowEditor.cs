using System.Collections.Generic;
using System.IO;
using System.Text;
using UnityEditor;
using UnityEngine;

public class JenkinsSettingWindowEditor : EditorWindow
{
    private const string RootTools = "Tools/JenkinsPipeline/";

    [MenuItem(RootTools + "Edit Config")]
    public static void ShowWindow()
    {
        EditorWindow.GetWindow(typeof(JenkinsSettingWindowEditor));
    }
    
    List<Config> configs;

    private class Config
    {
        public string Key;
        public string Value;
    }

    private Vector2 scrollPos;
    private const string HelperInfo = @"BUILD_METHOD_NAME: static method that will be called from batchmode
SLACK_BOT_TOKEN: slack API token to send result as Bot (optional)
SLACK_DEFAULT_CHANNEL: all build file will be send through here and attachments. All failed build will be send directly to commiter (optional)
BUILD_BASE_BUNDLE_VERSION: build bundle version from CI will automatic increase from this value (optional)

PRODUCTION_BUILD_METHOD_NAME: any branch name contains 'production' will be tag as PRODUCTION and call this method
DEVELOP_BUILD_METHOD_NAME: any branch name contains 'develop' will be tag as DEVELOP and call this method
other branch will call method from INTERNAL_BUILD_METHOD_NAME

For other configs added during CI step. Read doc from package";

    private void Awake() { configs = ReadConfigFiles(); }


    List<Config> ReadConfigFiles()
    {
        string configFile = GetConfigFilePath();
        var lines      = File.ReadAllLines(configFile);
        var configs    = new List<Config>(lines.Length);
        
        foreach (string line in lines) {
            var    splits = line.Split('=');
            string key    = splits[0];
            string value  = splits.Length > 1 ? splits[1] : null;
            configs.Add(new Config(){Key = key,Value = value});
        }

        return configs;
    }

    private string GetConfigFilePath()
    {
        var projectDir = new DirectoryInfo(Application.dataPath).Parent;
        var configFile = Path.Combine(projectDir.FullName, "config.cfg");
        return configFile;
    }

    

    
    private void OnGUI()
    {
        scrollPos = GUILayout.BeginScrollView(scrollPos);
        GUILayout.Label("Config file: " + GetConfigFilePath());
        EditorGUILayout.HelpBox( HelperInfo, MessageType.Info);
        
        
        
        if (configs       == null ||
            configs.Count == 0) {
            GUILayout.Label("Empty config files. CI might not working properly", EditorStyles.boldLabel);
            // Update every frame is alright
            configs = ReadConfigFiles();
            return;
        }

        int count = configs.Count;
        float positionWidth = position.width - 40f;
        for (var i = 0; i < count; i++) {
            var config = configs[i];
            GUILayout.BeginHorizontal();
            config.Key   = GUILayout.TextField(config.Key,   GUILayout.Width(positionWidth / 2f));
            config.Value = GUILayout.TextField(config.Value, GUILayout.Width(positionWidth / 2f));
            if (GUILayout.Button("X", GUILayout.Width(20f))) {
                configs.RemoveAt(i);
                i--;
                count--;
            }
            GUILayout.EndHorizontal();
        }
        

        GUILayout.BeginHorizontal();
        if (GUILayout.Button("Revert file")) configs = ReadConfigFiles();
        if (GUILayout.Button("Apply Changes")) { WriteConfigFile(); }
        GUILayout.EndHorizontal();
        
        GUILayout.EndScrollView();
    }

    // Write to shell .cfg format
    private void WriteConfigFile()
    {
        var filePath = GetConfigFilePath();
        var contentBuilder = new StringBuilder();
        foreach (var config in configs) {
            // Make sure space string contains quote.
            string configValue = config.Value;
            if (configValue.Contains(" ")  && !configValue.StartsWith("\"") && !configValue.EndsWith("\"")) 
            {
                config.Value = $"\"{configValue}\"";
            }
            contentBuilder.AppendLine($"{config.Key}={configValue}");
        }
        File.WriteAllText(filePath,contentBuilder.ToString());
        configs = ReadConfigFiles();
    }
}