#Requires -RunAsAdministrator
<#
.SYNOPSIS
    .
.DESCRIPTION
    .
.PARAMETER unityPath
    Full or absolute path to unity.exe file. Remeber put path in quote mark "". Ex: -unityPath "C:\Program Files\Unity\Hub\Editor\2019.2.1f1\Editor\Unity"
.PARAMETER logFile
    absolute path or just file name. Will join file name with current path if not full path.
.PARAMETER method
    Unity file and method function to call build. Normally static editor class function. Defautl: "Builder.Build"
.PARAMETER username
    Unity username account. dont use this if you already license unity on local machine
.PARAMETER password
    Unity password account. dont use this if you already license unity on local machine
.PARAMETER params
    Any extra args or other params you want to pass in Unity. It just add string to arguments call. So becareful for error format. Ex: -params "-RANDOM_VARIABLE "VAR1" -SWITCH_VARIABLE -FORCE_SOMETHING"
.PARAMETER arguments
    Unity batchmode cli command. Default: "-quit -batchmode". You can change it to "-quit -batchmode -accept-apiupdate"
.PARAMETER gitLog
    Call git log author and commit name from current folder and assign them to variable like GIT_AUHTOR, GIT_COMMITTER and add them to arguments.
    https://git-scm.com/docs/pretty-formats
.EXAMPLE
    ./unity.ps1 -unityPath "C:\Program Files\Unity\Hub\Editor\2019.2.1f1\Editor\Unity.exe"  -method "BuildCommandClass.BuildDebug" -addGitLog
#>
param (
    [Alias("unity")][string]$unityPath,
    [Alias("log")][string]$logFile = "log.txt",
    [Alias("target")][string]$buildTarget = "Win64",
    [string]$unityProject,
    [string]$method = "Builder.Build",
    [string]$username, # not really needed if unity already activate through manual license
    [string]$password,
    [Alias("param")][string]$params, #any extra text to add in argurments
    [Alias("arg", "args")][string]$arguments = "-quit -batchmode",
    [Alias("gitLog", "git", "addGitLog")][switch]$addGitLog # add author name, commit date, etc
)

if (!$unityPath)
{
    Get-Help $MyInvocation.MyCommand.Definition
    return
}

if (![System.IO.File]::Exists($unityPath))
{
    Write-Error "this unity path did not exist: " $unityPath
    exit 1;
}

if ( [string]::IsNullOrEmpty($unityProject))
{
    Write-Host "Use current path as project folder: $PWD"
    $unityProject = pwd
}

$stringbuilder = New-Object -TypeName System.Text.StringBuilder

[void]$stringbuilder.Append($arguments)

function AddArgument
{
    Param([string]$x, [string]$y)
    if ($x -and $y)
    {
        [void]$stringbuilder.AppendFormat(" -{0} `"{1}`"", $x, $y)
    }
}

if (![System.IO.Path]::IsPathRooted($logFile))
{
    $logFile = Join-Path $unityProject $logFile
}

AddArgument "username"  $username
AddArgument "password"  $password
AddArgument "buildTarget "  $buildTarget
AddArgument "logFile" $logFile
AddArgument "projectPath" $unityProject
AddArgument "executeMethod"  $method

[void]$stringbuilder.AppendFormat(" {0} ", $params)


function AddGitArgument
{
    Param([string]$x, [string]$y)
    if ($x -and $y)
    {
        $y = "git log -1 --pretty=format:%$y"
        $y = Invoke-Expression $y
        [void]$stringbuilder.AppendFormat(" -{0} `"{1}`"", $x, $y)
    }
}

if ($addGitLog)
{
    # https://git-scm.com/docs/pretty-formats
    AddGitArgument GIT_AUTHOR_EMAIL ae
    AddGitArgument GIT_AUTHOR_NAME an
    AddGitArgument GIT_AUTHOR an
    AddGitArgument GIT_COMMIT_HASH H
    AddGitArgument GIT_COMMIT_SHORT_HASH h
    AddGitArgument GIT_TREE_HASH T
    AddGitArgument GIT_AUTHOR_DATE aD #author date, RFC2822 style
    AddGitArgument GIT_COMMITER_NAME cn
    AddGitArgument GIT_COMMITER cn
    AddGitArgument GIT_COMMITER_EMAIL ce
    AddGitArgument GIT_COMMITER_DATE cD
    AddGitArgument GIT_SUBJECT s #first line of git message
    AddGitArgument GIT_BODY b
    AddGitArgument GIT_RAW_BODY B
    AddArgument "GIT_BRANCH"  (git log -n 1 --pretty = %d | cut -d / -f 2 | sed -r 's/[)]+//g')
}


# the run command look something like this
# $unity   -logfile "$logFile" `
#          -executeMethod SuperSystems.UnityBuild.BuildCLI.PerformBuild `
#          -quit `
#          -batchmode `
#          -username vaddummy@vadomain.com `
#          -password Vaddummy123 `

# Must run unity from new powershell so it excute on another thread => Not blocking jenkins if fail

$arguments = $stringbuilder.ToString()
Write-Host "Run unity with arguments:" $unityPath $arguments
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