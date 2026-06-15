param(
    [string]$Version = "1.2.0"
)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$releaseRoot = Join-Path $repoRoot "release"
$packageName = "W-MIDI-v$Version"
$packageRoot = Join-Path $releaseRoot $packageName
$distRoot = Join-Path $releaseRoot ".portable-dist"
$workRoot = Join-Path $releaseRoot ".pyinstaller-build"
$specRoot = Join-Path $releaseRoot ".pyinstaller-spec"
$entryPoint = Join-Path $repoRoot "midi_wled_bridge\frozen_entry.py"
$icon = Join-Path $repoRoot "assets\windows\w-midi.ico"
$localSitePackages = Join-Path $repoRoot ".runtime\site-packages"

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
Remove-ReleaseChild $distRoot
Remove-ReleaseChild $workRoot
Remove-ReleaseChild $specRoot

New-Item -ItemType Directory -Path $releaseRoot -Force | Out-Null

& pyinstaller `
    --noconfirm `
    --clean `
    --onedir `
    --windowed `
    --contents-directory "_internal" `
    --name "W-MIDI" `
    --icon $icon `
    --paths $localSitePackages `
    --hidden-import "rtmidi" `
    --hidden-import "mido.backends.rtmidi" `
    --distpath $distRoot `
    --workpath $workRoot `
    --specpath $specRoot `
    $entryPoint

if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller failed with exit code $LASTEXITCODE."
}

Copy-Item -LiteralPath (Join-Path $distRoot "W-MIDI") -Destination $packageRoot -Recurse -Force

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

Remove-ReleaseChild $distRoot
Remove-ReleaseChild $workRoot
Remove-ReleaseChild $specRoot

Write-Host "Created portable folder $packageRoot"
