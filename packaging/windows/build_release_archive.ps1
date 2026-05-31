param(
    [string]$Version = "1.1.0"
)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$releaseRoot = Join-Path $repoRoot "release"
$packageName = "W-MIDI-v$Version"
$packageRoot = Join-Path $releaseRoot $packageName
$archivePath = Join-Path $releaseRoot "$packageName.zip"
$portableBuilder = Join-Path $PSScriptRoot "build_portable_release.ps1"

& powershell -ExecutionPolicy Bypass -File $portableBuilder -Version $Version
if ($LASTEXITCODE -ne 0) {
    throw "Portable release build failed with exit code $LASTEXITCODE."
}

if (Test-Path -LiteralPath $archivePath) {
    Remove-Item -LiteralPath $archivePath -Force
}

Compress-Archive -Path $packageRoot -DestinationPath $archivePath -Force
Write-Host "Created $archivePath"
