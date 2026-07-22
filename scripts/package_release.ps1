$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$version = "0.1.0"
$distDir = Join-Path $repoRoot "dist\BookletSplitter"
$releaseDir = Join-Path $repoRoot "release"
$zipPath = Join-Path $releaseDir "BookletSplitter-v$version-windows-x64.zip"

if (-not (Test-Path -LiteralPath $distDir)) {
  throw "Build output not found: $distDir. Run .\scripts\build_windows.ps1 first."
}

if (-not (Test-Path -LiteralPath $releaseDir)) {
  New-Item -ItemType Directory -Path $releaseDir | Out-Null
}

if (Test-Path -LiteralPath $zipPath) {
  Remove-Item -LiteralPath $zipPath -Force
}

Compress-Archive -LiteralPath $distDir -DestinationPath $zipPath -CompressionLevel Optimal
Write-Host "Wrote $zipPath"
