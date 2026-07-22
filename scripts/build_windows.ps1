$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$venvDir = Join-Path $repoRoot ".venv-build"
$python = Join-Path $venvDir "Scripts\python.exe"

if (-not (Test-Path -LiteralPath $python)) {
  python -m venv $venvDir
}

& $python -m pip install --upgrade pip
& $python -m pip install -e "."
& $python -m pip install "pyinstaller>=6"
& $python -m PyInstaller `
  --clean `
  --noconfirm `
  --windowed `
  --name BookletSplitter `
  --collect-data booklet_splitter `
  --exclude-module PyQt5 `
  --exclude-module PyQt6 `
  --exclude-module PySide6 `
  "src\booklet_splitter\__main__.py"
