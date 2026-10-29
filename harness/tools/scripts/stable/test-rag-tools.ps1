param([string]$Root = '.')
$ErrorActionPreference = 'Stop'
$rootPath = (Resolve-Path -LiteralPath $Root).Path
$python = Join-Path $rootPath 'var/rag/venvs/llm-wiki-agent/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $python)) { $python = 'python' }
$oldPythonPath = $env:PYTHONPATH
$oldPythonUtf8 = $env:PYTHONUTF8
try {
    $env:PYTHONPATH = Join-Path $rootPath 'harness/tools/scripts/stable'
    $env:PYTHONUTF8 = '1'
    & $python -m unittest discover -s (Join-Path $rootPath 'harness/tools/tests') -p 'test_rag_*.py' -v
    exit $LASTEXITCODE
} finally {
    $env:PYTHONPATH = $oldPythonPath
    $env:PYTHONUTF8 = $oldPythonUtf8
}
