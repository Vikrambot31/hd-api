param(
  [string]$PythonExe = "python"
)

# Setup: encoding and error handling

# ЭТАП 5: принудительная UTF-8 кодировка
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding  = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$ErrorActionPreference = "Continue"

$port = 8000
$apiPort = 10000
# ЭТАП 6: нормализация путей
$projectPath = $PSScriptRoot
$url = "http://localhost:$port/calculator_web.html"
$listener = $null
$pythonProcess = $null

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Human Design Web Calculator - Local Server" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

function Test-ApiHealth {
  param([string]$ApiUrl)
  try {
    $resp = Invoke-WebRequest -Uri $ApiUrl -Method Get -TimeoutSec 2 -UseBasicParsing
    return ($resp.StatusCode -ge 200 -and $resp.StatusCode -lt 500)
  }
  catch {
    return $false
  }
}

function Get-ContentType {
  param([string]$Path)
  switch ([IO.Path]::GetExtension($Path).ToLowerInvariant()) {
    ".html" { "text/html; charset=utf-8" }
    ".js" { "application/javascript; charset=utf-8" }
    ".json" { "application/json; charset=utf-8" }
    ".css" { "text/css; charset=utf-8" }
    ".svg" { "image/svg+xml" }
    ".png" { "image/png" }
    ".jpg" { "image/jpeg" }
    ".jpeg" { "image/jpeg" }
    ".gif" { "image/gif" }
    ".txt" { "text/plain; charset=utf-8" }
    default { "application/octet-stream" }
  }
}

function Write-Response {
  param([Parameter(Mandatory=$true)]$Response, [Parameter(Mandatory=$true)][int]$StatusCode, [byte[]]$Bytes, [string]$ContentType="application/octet-stream")
  $Response.StatusCode = $StatusCode
  $Response.ContentType = $ContentType
  if ($Bytes) {
    $Response.ContentLength64 = $Bytes.Length
    $Response.OutputStream.Write($Bytes, 0, $Bytes.Length)
  }
  $Response.OutputStream.Close()
}

Write-Host "[1/3] Starting Python API (port $apiPort)..." -ForegroundColor Cyan

# ЭТАП 7: все пути через Join-Path
$pythonScriptPath = Join-Path $projectPath "hd_api.py"
$apiUrl = "http://localhost:$apiPort/"
$ownsPythonProcess = $false
if (-not (Test-Path $pythonScriptPath)) {
  Write-Host "ERROR: hd_api.py not found at $pythonScriptPath" -ForegroundColor Red
  exit 1
}

if (Test-ApiHealth -ApiUrl $apiUrl) {
  Write-Host "  OK: Python API already running, reusing existing process" -ForegroundColor Green
}
else {
  try {
    $apiLogPath = Join-Path $projectPath "hd_api_start.log"
    if (Test-Path $apiLogPath) {
      Remove-Item $apiLogPath -Force -ErrorAction SilentlyContinue
    }

    # ЭТАП 8: запуск Python с правильной обработкой пути
    $pythonProcess = Start-Process -FilePath $PythonExe -ArgumentList "`"$pythonScriptPath`"" -WorkingDirectory $projectPath -WindowStyle Hidden -PassThru -RedirectStandardError $apiLogPath
    $ownsPythonProcess = $true
    Write-Host "  OK: Python API started (PID: $($pythonProcess.Id))" -ForegroundColor Green
    Start-Sleep -Milliseconds 2200

    if ($pythonProcess.HasExited -and -not (Test-ApiHealth -ApiUrl $apiUrl)) {
      Write-Host "  ERROR: Python API exited before becoming healthy" -ForegroundColor Red
      if (Test-Path $apiLogPath) {
        Write-Host "  --- hd_api_start.log ---" -ForegroundColor Yellow
        Get-Content $apiLogPath -TotalCount 40
        Write-Host "  ------------------------" -ForegroundColor Yellow
      }
      exit 1
    }
  }
  catch {
    Write-Host "  ERROR: Could not start Python API with interpreter: $PythonExe" -ForegroundColor Red
    exit 1
  }
}

Write-Host "[2/3] Starting HTTP server (port $port)..." -ForegroundColor Cyan
try {
  $listener = New-Object System.Net.HttpListener
  $listener.Prefixes.Add("http://localhost:$port/")
  $listener.Start()
  Write-Host "  OK: HTTP server started" -ForegroundColor Green
} catch {
  Write-Host "  ERROR: Could not start HTTP server (port may be in use)" -ForegroundColor Red
  if ($pythonProcess -and -not $pythonProcess.HasExited) { $pythonProcess.Kill() }
  exit 1
}

Write-Host "[3/3] Opening browser..." -ForegroundColor Cyan
Start-Process $url
Write-Host "  OK: Browser opened: $url" -ForegroundColor Green

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "  Servers running successfully!" -ForegroundColor Green
Write-Host "  • Static: http://localhost:$port/" -ForegroundColor Cyan
Write-Host "  • API:    http://localhost:$apiPort/" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

try {
  while ($listener.IsListening) {
    $context = $listener.GetContext()
    $request = $context.Request
    $response = $context.Response

    try {
      $relativePath = [System.Uri]::UnescapeDataString($request.Url.AbsolutePath).TrimStart('/')
      if ([string]::IsNullOrWhiteSpace($relativePath)) { $relativePath = "calculator_web.html" }
      
      $relativePath = $relativePath.Replace("/", "\")
      $fullPath = [IO.Path]::GetFullPath((Join-Path $projectPath $relativePath))
      $rootPath = [IO.Path]::GetFullPath($projectPath)

      if (-not $fullPath.StartsWith($rootPath)) {
        Write-Response $response 403 ([Text.Encoding]::UTF8.GetBytes("403 Forbidden")) "text/plain; charset=utf-8"
        continue
      }

      if ((Test-Path $fullPath) -and (Get-Item $fullPath).PSIsContainer) {
        $fullPath = Join-Path $fullPath "calculator_web.html"
      }

      if (-not (Test-Path $fullPath)) {
        Write-Response $response 404 ([Text.Encoding]::UTF8.GetBytes("404 Not Found")) "text/plain; charset=utf-8"
        continue
      }

      $bytes = [IO.File]::ReadAllBytes($fullPath)
      $ct = Get-ContentType $fullPath
      Write-Response $response 200 $bytes $ct
    } catch {
      $msg = "500 Internal Server Error`r`n$($_.Exception.Message)"
      Write-Response $response 500 ([Text.Encoding]::UTF8.GetBytes($msg)) "text/plain; charset=utf-8"
    }
  }
} finally {
  Write-Host ""
  Write-Host "Shutting down..." -ForegroundColor Yellow
  if ($listener) { $listener.Stop(); $listener.Close() }
  if ($ownsPythonProcess -and $pythonProcess -and -not $pythonProcess.HasExited) {
    $pythonProcess.Kill()
    $pythonProcess.WaitForExit()
  }
  Write-Host "Done." -ForegroundColor Green
}
