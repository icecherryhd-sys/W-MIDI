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
$nuitkaRoot = Join-Path $releaseRoot ".nuitka-build"
$nuitkaCacheRoot = Join-Path $releaseRoot ".nuitka-cache"
$entryPoint = Join-Path $repoRoot "midi_wled_bridge\frozen_entry.py"
$icon = Join-Path $repoRoot "assets\windows\w-midi.ico"
$localSitePackages = Join-Path $repoRoot ".runtime\site-packages"

function Invoke-BuildPython([string[]]$Arguments) {
    if ($PythonExe) {
        if (-not (Test-Path -LiteralPath $PythonExe)) {
            throw "Python executable not found: $PythonExe"
        }
        & $PythonExe @Arguments
        return
    }
    & py "-$PythonVersion" @Arguments
}

function Remove-ReleaseChild([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path)) {
        return
    }
    $resolvedPath = (Resolve-Path -LiteralPath $Path).Path
    if (-not $resolvedPath.StartsWith($releaseRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to remove a folder outside the release directory: $resolvedPath"
    }
    Remove-Item -LiteralPath $resolvedPath -Recurse -Force
}

Remove-ReleaseChild $packageRoot
Remove-ReleaseChild $nuitkaRoot

New-Item -ItemType Directory -Path $releaseRoot -Force | Out-Null
New-Item -ItemType Directory -Path $nuitkaCacheRoot -Force | Out-Null
$env:NUITKA_CACHE_DIR = $nuitkaCacheRoot

$nuitkaArgs = @(
    "--standalone",
    "--assume-yes-for-downloads",
    "--enable-plugin=pyside6",
    "--windows-console-mode=disable",
    "--windows-icon-from-ico=$icon",
    "--include-module=rtmidi",
    "--include-module=mido.backends.rtmidi",
    "--include-package=serial",
    "--output-filename=W-MIDI.exe",
    "--output-dir=$nuitkaRoot"
)

if (Test-Path -LiteralPath $localSitePackages) {
    $nuitkaArgs += "--python-flag=-S"
    $env:PYTHONPATH = "$localSitePackages;$repoRoot;$env:PYTHONPATH"
}

$nuitkaArgs += $entryPoint

$buildPythonArgs = @("-m", "nuitka") + $nuitkaArgs
Invoke-BuildPython $buildPythonArgs
if ($LASTEXITCODE -ne 0) {
    throw "Nuitka failed with exit code $LASTEXITCODE."
}

$distFolder = Get-ChildItem -LiteralPath $nuitkaRoot -Directory -Filter "*.dist" |
    Select-Object -First 1
if ($null -eq $distFolder) {
    throw "Nuitka did not create a .dist folder in $nuitkaRoot."
}

Copy-Item -LiteralPath $distFolder.FullName -Destination $packageRoot -Recurse -Force

$visibleFiles = @(
    "W-MIDI Tutorial Guide.pdf",
    "README.md",
    "README_EN.txt",
    "README.txt",
    "LICENSE.txt",
    "CHANGELOG.md",
    "config.example.json",
    "assets",
    "layouts",
    "palettes"
)

foreach ($relativePath in $visibleFiles) {
    $source = Join-Path $repoRoot $relativePath
    if (-not (Test-Path -LiteralPath $source)) {
        throw "Required release file is missing: $relativePath"
    }
    Copy-Item -LiteralPath $source -Destination $packageRoot -Recurse -Force
}

Remove-ReleaseChild $nuitkaRoot

Write-Host "Created Nuitka portable folder $packageRoot"
