# Starts the ATS Resume Tracker FastAPI server directly (no desktop browser window),
# detached from this shell, tracked via server.pid for server-stop.ps1 to find later.
$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

$port = 8765
$pidFile = Join-Path $root "server.pid"
$venvPython = Join-Path $root ".venv\Scripts\python.exe"
$logFile = Join-Path $root "server.log"
$errLogFile = Join-Path $root "server.err.log"

if (-not (Test-Path $venvPython)) {
    Write-Error "Virtual environment not found at $venvPython. Run run.bat once first to set it up."
    exit 1
}

# Already tracked and alive?
if (Test-Path $pidFile) {
    $existingPid = Get-Content $pidFile -ErrorAction SilentlyContinue
    if ($existingPid -and (Get-Process -Id $existingPid -ErrorAction SilentlyContinue)) {
        Write-Host "Server already running (PID $existingPid) at http://127.0.0.1:$port"
        exit 0
    }
    Remove-Item $pidFile -Force -ErrorAction SilentlyContinue
}

# Something else already bound to the port?
$existingListener = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
if ($existingListener) {
    Write-Host "Port $port is already in use by PID $($existingListener.OwningProcess) (not started by this script). Not starting a new instance."
    exit 1
}

$proc = Start-Process -FilePath $venvPython `
    -ArgumentList @("-m", "uvicorn", "app.server:app", "--host", "127.0.0.1", "--port", "$port") `
    -WorkingDirectory $root `
    -RedirectStandardOutput $logFile `
    -RedirectStandardError $errLogFile `
    -WindowStyle Hidden `
    -PassThru

Start-Sleep -Seconds 2

if (Get-Process -Id $proc.Id -ErrorAction SilentlyContinue) {
    Set-Content -Path $pidFile -Value $proc.Id -NoNewline
    Write-Host "Server started (PID $($proc.Id)) at http://127.0.0.1:$port"
    Write-Host "Logs: $logFile"
} else {
    Write-Error "Server failed to start. Check $errLogFile for details."
    exit 1
}
