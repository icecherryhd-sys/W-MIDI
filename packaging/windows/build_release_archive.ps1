param(
    [string]$Version = "1.2.0",
    [string]$PythonVersion = "3.12",
    [string]$PythonExe = ""
)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$releaseRoot = Join-Path $repoRoot "release"
$packageName = "W-MIDI-v$Version"
$packageRoot = Join-Path $releaseRoot $packageName
$archivePath = Join-Path $releaseRoot "$packageName.zip"
$portableBuilder = Join-Path $PSScriptRoot "build_nuitka_release.ps1"

$builderArgs = @(
    "-ExecutionPolicy", "Bypass",
    "-File", $portableBuilder,
    "-Version", $Version,
    "-PythonVersion", $PythonVersion
)
if ($PythonExe) {
    $builderArgs += @("-PythonExe", $PythonExe)
}

& powershell @builderArgs
if ($LASTEXITCODE -ne 0) {
    throw "Nuitka release build failed with exit code $LASTEXITCODE."
}

if (Test-Path -LiteralPath $archivePath) {
    Remove-Item -LiteralPath $archivePath -Force
}

Compress-Archive -Path $packageRoot -DestinationPath $archivePath -Force
Write-Host "Created $archivePath"
