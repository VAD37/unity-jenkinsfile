#/Requires -RunAsAdministrator
<#
.SYNOPSIS
    Custom script to run Unity build in special CI env.
    Due to Unity batchmode on Windows not run too well with JDK, NDK. This script prevent floating unity.exe failed to kill process. (this is Jenkins error due to new Unity process not call as sub-process)
.PARAMETER configFile
    absolute path or just file name. Will join file name with current path if not full path.
#>
param (
    [Alias("config")][string]$configFile
)


if (![System.IO.File]::Exists($configFile))
{
    Write-Error "this config file did not exist: $configFile" 
    exit 1;
}

Get-Content $configFile | foreach-object -begin {$table=@{}} -process { $k = [regex]::split($_,'='); if(($k[0].CompareTo("") -ne 0) -and ($k[0].StartsWith("[") -ne $True)) { $table.Add($k[0], $k[1]) } }

$unityPath = $table["UNITY_PATH"]

$stringbuilder = New-Object -TypeName System.Text.StringBuilder

# Find arg in Env or config find. then append to unity as command line
function AddArgumentIfFound
{
    Param([string]$argName, [string]$variable)
    if ([Environment]::GetEnvironmentVariable($variable))
    {
        [void]$stringbuilder.AppendFormat(" -{0} `"{1}`"", $argName, [Environment]::GetEnvironmentVariable($variable))
    }
    elseif ($table.ContainsKey($variable))
    {        
        [void]$stringbuilder.AppendFormat(" -{0} {1}", $argName, $table["$variable"])
    }
}


foreach ($arg in $args)
{
    [void]$stringbuilder.AppendFormat(" {0} ", $arg)
}

AddArgumentIfFound "buildTarget "  "BUILD_TARGET"
AddArgumentIfFound "logFile" "UNITY_BUILD_LOG"
AddArgumentIfFound "projectPath" "UNITY_PROJECT"
AddArgumentIfFound "executeMethod"  "BUILD_METHOD_NAME"

if ($table.ContainsKey("UNITY_BUILD_PARAMS"))
{ 
    [void]$stringbuilder.AppendFormat(" {0} ", $table["UNITY_BUILD_PARAMS"].ToString().Trim('"'))
}


# Must run unity from new powershell so it excute as sub process => Jenkins can end process if Unity timeout or failure
# Gradle build + il2cpp with unity on Windows have some very weird bugs that block CI if it have very specific compiler error.

$arguments = $stringbuilder.ToString()
Write-Host "command line:" $unityPath $arguments
$pinfo = New-Object System.Diagnostics.ProcessStartInfo
$pinfo.FileName = $unityPath
$pinfo.RedirectStandardError = $true
$pinfo.RedirectStandardOutput = $true
$pinfo.UseShellExecute = $false
$pinfo.Arguments = "$arguments"
$p = New-Object System.Diagnostics.Process
$p.StartInfo = $pinfo
$p.Start() | Out-Null
$p.WaitForExit()

$stdout = $p.StandardOutput.ReadToEnd()
$stderr = $p.StandardError.ReadToEnd()
Write-Host "exit code: " + $p.ExitCode
Write-Output "$stdout"
if ($stderr)
{
    Write-Error "$stderr"
}
exit $p.ExitCode