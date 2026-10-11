param(
    [string]$PythonExecutable
)

$ErrorActionPreference = "Stop"

$originalLocation = Get-Location
$repositoryRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path

if ([string]::IsNullOrWhiteSpace($PythonExecutable)) {
    $virtualEnvironmentPython = Join-Path $repositoryRoot "ecommerce\backend\.venv\Scripts\python.exe"
    if (Test-Path -LiteralPath $virtualEnvironmentPython) {
        $PythonExecutable = $virtualEnvironmentPython
    }
    else {
        $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
        if ($null -eq $pythonCommand) {
            throw "Python was not found. Install backend dependencies or pass -PythonExecutable <path>."
        }
        $PythonExecutable = $pythonCommand.Source
    }
}

if (-not (Test-Path -LiteralPath $PythonExecutable)) {
    throw "Python executable does not exist: $PythonExecutable"
}

try {
    Set-Location -LiteralPath $repositoryRoot
    & $PythonExecutable scripts/check_structure.py
    if ($LASTEXITCODE -ne 0) {
        throw "Directory structure check failed with exit code $LASTEXITCODE"
    }

    Set-Location -LiteralPath (Join-Path $repositoryRoot "ecommerce\frontend")
    & npm run check
    if ($LASTEXITCODE -ne 0) {
        throw "Frontend quality gate failed with exit code $LASTEXITCODE"
    }

    Set-Location -LiteralPath (Join-Path $repositoryRoot "ecommerce\backend")
    & $PythonExecutable -c "import sys; assert sys.version_info >= (3, 11), 'Python 3.11 or newer is required'; import pytest, alembic"
    if ($LASTEXITCODE -ne 0) {
        throw "Backend Python preflight failed. Install requirements.txt or pass -PythonExecutable <path> to a prepared environment."
    }

    & $PythonExecutable -m compileall -q app
    if ($LASTEXITCODE -ne 0) {
        throw "Backend compile check failed with exit code $LASTEXITCODE"
    }

    & $PythonExecutable -m pytest
    if ($LASTEXITCODE -ne 0) {
        throw "Backend tests failed with exit code $LASTEXITCODE"
    }

    & $PythonExecutable -m alembic heads
    if ($LASTEXITCODE -ne 0) {
        throw "Alembic head check failed with exit code $LASTEXITCODE"
    }
}
finally {
    Set-Location -LiteralPath $originalLocation
}
