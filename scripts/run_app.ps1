$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$srcPath = Join-Path $repoRoot "src"
$env:PYTHONPATH = "$srcPath;$env:PYTHONPATH"

python -m booklet_print_layout_assistant
