# Stops the ATS Resume Tracker FastAPI server started by server-start.ps1.
# Falls back to killing whatever is listening on the port, in case the PID file
# is stale or the server was started another way.
$ErrorActionPreference = "SilentlyContinue"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

$port = 8765
$pidFile = Join-Path $root "server.pid"
$stopped = $false

if (Test-Path $pidFile) {
    $savedPid = Get-Content $pidFile
    if ($savedPid -and (Get-Process -Id $savedPid -ErrorAction SilentlyContinue)) {
        Stop-Process -Id $savedPid -Force
        Write-Host "Stopped server (PID $savedPid)."
        $stopped = $true
    }
    Remove-Item $pidFile -Force
}

$listeners = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
foreach ($listener in $listeners) {
    Stop-Process -Id $listener.OwningProcess -Force -ErrorAction SilentlyContinue
    if ($?) {
        Write-Host "Stopped process PID $($listener.OwningProcess) listening on port $port."
        $stopped = $true
    }
}

if (-not $stopped) {
    Write-Host "No running server found on port $port."
}
