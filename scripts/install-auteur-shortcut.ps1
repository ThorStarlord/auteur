param(
  [string]$ShortcutPath = "$([Environment]::GetFolderPath('Desktop'))\Auteur.lnk"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$Launcher = Join-Path $RepoRoot "Auteur.cmd"

if (-not (Test-Path $Launcher)) {
  throw "Auteur launcher not found: $Launcher"
}

$Shell = New-Object -ComObject WScript.Shell
$Shortcut = $Shell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $Launcher
$Shortcut.WorkingDirectory = $RepoRoot
$Shortcut.Description = "Open Auteur"
$Shortcut.Save()

Write-Host "Created Auteur shortcut: $ShortcutPath"
