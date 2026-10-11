param(
    [string]$PythonExecutable,
    [string]$PostgresBin,
    [ValidateRange(1024, 65535)][int]$DatabasePort = 55432,
    [ValidateRange(1024, 65535)][int]$ApiPort = 8000
)

$ErrorActionPreference = 'Stop'
$repositoryRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$backendRoot = Join-Path $PSScriptRoot 'backend'
$runtimeRoot = Join-Path $repositoryRoot 'output\local-runtime'
$dataRoot = Join-Path $runtimeRoot 'postgres'
$venvPython = Join-Path $backendRoot '.venv\Scripts\python.exe'
New-Item -ItemType Directory -Path $runtimeRoot -Force | Out-Null

if ([string]::IsNullOrWhiteSpace($PostgresBin)) {
    $postgresCommand = Get-Command postgres.exe -ErrorAction SilentlyContinue
    if ($postgresCommand) {
        $PostgresBin = Split-Path $postgresCommand.Source
    }
    else {
        $installation = Get-ChildItem -LiteralPath 'C:\Program Files\PostgreSQL' -Directory -ErrorAction SilentlyContinue |
            Sort-Object { [int]$_.Name } -Descending | Select-Object -First 1
        if ($installation) { $PostgresBin = Join-Path $installation.FullName 'bin' }
    }
}
if (-not $PostgresBin -or -not (Test-Path -LiteralPath (Join-Path $PostgresBin 'postgres.exe'))) {
    throw 'Install PostgreSQL 16+ or pass -PostgresBin C:\path\to\PostgreSQL\bin. Docker users can use start.bat.'
}

if (-not (Test-Path -LiteralPath $venvPython)) {
    if ([string]::IsNullOrWhiteSpace($PythonExecutable)) {
        $bundledPython = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
        if (Test-Path -LiteralPath $bundledPython) { $PythonExecutable = $bundledPython }
        else {
            $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
            if ($pythonCommand) { $PythonExecutable = $pythonCommand.Source }
        }
    }
    if (-not $PythonExecutable) { throw 'Python 3.11+ is required. Pass -PythonExecutable C:\path\to\python.exe.' }
    & $PythonExecutable -c "import sys; assert sys.version_info >= (3, 11), 'Python 3.11+ is required'"
    if ($LASTEXITCODE -ne 0) { throw 'Pass -PythonExecutable with a Python 3.11+ interpreter.' }
    $uvCommand = Get-Command uv -ErrorAction SilentlyContinue
    if ($uvCommand) {
        & $uvCommand.Source venv --python $PythonExecutable --cache-dir (Join-Path $runtimeRoot 'uv-cache') (Join-Path $backendRoot '.venv')
    }
    else { & $PythonExecutable -m venv (Join-Path $backendRoot '.venv') }
    if ($LASTEXITCODE -ne 0) { throw 'Could not create the backend virtual environment.' }
}

& $venvPython -c 'import fastapi, uvicorn, asyncpg, alembic, pytest' 2>$null
if ($LASTEXITCODE -ne 0) {
    $uvCommand = Get-Command uv -ErrorAction SilentlyContinue
    if ($uvCommand) {
        & $uvCommand.Source pip install --python $venvPython --cache-dir (Join-Path $runtimeRoot 'uv-cache') -r (Join-Path $backendRoot 'requirements.txt')
    }
    else { & $venvPython -m pip install -r (Join-Path $backendRoot 'requirements.txt') }
    if ($LASTEXITCODE -ne 0) { throw 'Backend dependency installation failed.' }
}

# This disposable development cluster stays inside the repository and listens
# only on loopback. Existing system PostgreSQL databases are never modified.
if (-not (Test-Path -LiteralPath (Join-Path $dataRoot 'PG_VERSION'))) {
    & (Join-Path $PostgresBin 'initdb.exe') -D $dataRoot -U pangchong --auth=trust --encoding=UTF8 --locale=C
    if ($LASTEXITCODE -ne 0) { throw 'Could not initialize the local development database.' }
}
& (Join-Path $PostgresBin 'pg_isready.exe') -h 127.0.0.1 -p $DatabasePort -q
if ($LASTEXITCODE -ne 0) {
    $postgresProcess = Start-Process -FilePath (Join-Path $PostgresBin 'postgres.exe') `
        -ArgumentList '-D', ('"' + $dataRoot + '"'), '-h', '127.0.0.1', '-p', $DatabasePort `
        -WindowStyle Hidden -PassThru `
        -RedirectStandardOutput (Join-Path $runtimeRoot 'postgres.stdout.log') `
        -RedirectStandardError (Join-Path $runtimeRoot 'postgres.stderr.log')
    $postgresProcess.Id | Set-Content -LiteralPath (Join-Path $runtimeRoot 'postgres.pid')
    for ($attempt = 0; $attempt -lt 30; $attempt++) {
        & (Join-Path $PostgresBin 'pg_isready.exe') -h 127.0.0.1 -p $DatabasePort -q
        if ($LASTEXITCODE -eq 0) { break }
        Start-Sleep -Milliseconds 500
    }
    if ($LASTEXITCODE -ne 0) { throw "PostgreSQL did not start. See $runtimeRoot\postgres.stderr.log" }
}

$psql = Join-Path $PostgresBin 'psql.exe'
$commonDbArgs = @('-h', '127.0.0.1', '-p', "$DatabasePort", '-U', 'pangchong', '-w', '-v', 'ON_ERROR_STOP=1')
$runningDataDirectory = (& $psql @commonDbArgs -d postgres -tAc 'SHOW data_directory').Trim()
if ($LASTEXITCODE -ne 0 -or [IO.Path]::GetFullPath($runningDataDirectory) -ne [IO.Path]::GetFullPath($dataRoot)) {
    throw "Port $DatabasePort belongs to a different database. Choose an unused -DatabasePort."
}
$databaseExists = & $psql @commonDbArgs -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname = 'pangchong_ecommerce'"
if ($databaseExists -ne '1') {
    & (Join-Path $PostgresBin 'createdb.exe') -h 127.0.0.1 -p $DatabasePort -U pangchong -w pangchong_ecommerce
    if ($LASTEXITCODE -ne 0) { throw 'Could not create the local application database.' }
}

$env:DATABASE_URL = "postgresql+asyncpg://pangchong@127.0.0.1:$DatabasePort/pangchong_ecommerce"
$env:APP_ENV = 'development'
$env:ALIPAY_SANDBOX = 'true'
$env:ASSET_STORAGE_BACKEND = 'local'
$env:PYTHONIOENCODING = 'utf-8'
Push-Location -LiteralPath $backendRoot
try {
    & $venvPython -m alembic upgrade head
    if ($LASTEXITCODE -ne 0) { throw 'Database migration failed.' }
    $productCount = & $psql @commonDbArgs -d pangchong_ecommerce -tAc 'SELECT count(*) FROM products'
    if ($productCount -eq '0') {
        & $psql @commonDbArgs -d pangchong_ecommerce -1 -f (Join-Path $PSScriptRoot 'database\seed.sql') -f (Join-Path $PSScriptRoot 'database\components.sql')
        if ($LASTEXITCODE -ne 0) { throw 'Demo data import failed; the seed transaction was rolled back.' }
    }
    $existingApi = $null
    try { $existingApi = Invoke-RestMethod "http://127.0.0.1:$ApiPort/health" -TimeoutSec 2 } catch { }
    if (-not $existingApi) {
        $backendProcess = Start-Process -FilePath $venvPython -WorkingDirectory $backendRoot `
            -ArgumentList '-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', $ApiPort `
            -WindowStyle Hidden -PassThru `
            -RedirectStandardOutput (Join-Path $runtimeRoot 'backend.stdout.log') `
            -RedirectStandardError (Join-Path $runtimeRoot 'backend.stderr.log')
        $backendProcess.Id | Set-Content -LiteralPath (Join-Path $runtimeRoot 'backend.pid')
        for ($attempt = 0; $attempt -lt 30; $attempt++) {
            try { $existingApi = Invoke-RestMethod "http://127.0.0.1:$ApiPort/health" -TimeoutSec 2; break } catch { }
            Start-Sleep -Milliseconds 500
        }
        if (-not $existingApi) { throw "API did not start. See $runtimeRoot\backend.stderr.log" }
    }
}
finally { Pop-Location }

Write-Host "API ready: http://localhost:$ApiPort/docs"
Write-Host 'Demo login: testuser / test123456 (admin uses the same password).'
Write-Host "Logs and local PostgreSQL data: $runtimeRoot"
Write-Host 'Frontend: cd ecommerce/frontend; npm install; npm run dev'
