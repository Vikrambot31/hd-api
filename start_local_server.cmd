@echo off
REM ═══════════════════════════════════════════════════════════════════════════
REM   Human Design Web Calculator - Local Server Launcher
REM ═══════════════════════════════════════════════════════════════════════════

chcp 65001 >nul
REM DO NOT enable delayed expansion - it breaks paths with '!' character
REM setlocal enabledelayedexpansion

REM ЭТАП 4: запуск из текущей директории
cd /d "%~dp0"

echo.
echo ======================================================================
echo         Human Design Web Calculator - Local Server Launcher
echo ======================================================================
echo.
echo Current directory: %CD%
echo.

REM ─── Выбор Python (venv приоритетно) ──────────────────────────────────────
set "PY_EXE=python"
if exist ".venv\Scripts\python.exe" (
    set "PY_EXE=%CD%\.venv\Scripts\python.exe"
)

REM ─── Проверка Python ───────────────────────────────────────────────────────
echo [1/4] Checking Python installation...
"%PY_EXE%" --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Python is not installed or not in PATH!
    echo.
    echo Solution:
    echo   1. Install Python from https://www.python.org/
    echo   2. During installation, CHECK "Add Python to PATH"
    echo.
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('"%PY_EXE%" --version') do set PYTHON_VER=%%i
echo   OK: %PYTHON_VER%

REM ─── Проверка файлов ──────────────────────────────────────────────────────
echo.
echo [2/4] Checking project files...

if not exist "start_local_server.ps1" (
    echo.
    echo ERROR: start_local_server.ps1 NOT FOUND!
    echo Expected location: %CD%\start_local_server.ps1
    echo.
    pause
    exit /b 1
)
echo   OK: start_local_server.ps1 found

if not exist "hd_api.py" (
    echo.
    echo ERROR: hd_api.py NOT FOUND!
    echo Expected location: %CD%\hd_api.py
    echo.
    pause
    exit /b 1
)
echo   OK: hd_api.py found

if not exist "requirements.txt" (
    echo.
    echo ERROR: requirements.txt NOT FOUND!
    echo Expected location: %CD%\requirements.txt
    echo.
    pause
    exit /b 1
)
echo   OK: requirements.txt found

REM ─── Проверка + установка зависимостей ────────────────────────────────────
echo.
echo [3/4] Installing/checking Python dependencies...
echo   (This may take a minute on first run)
"%PY_EXE%" -m pip install -q -r requirements.txt >nul 2>&1
if errorlevel 1 (
    echo.
    echo Trying with --user flag...
    "%PY_EXE%" -m pip install --user -q -r requirements.txt >nul 2>&1
    if errorlevel 1 (
        echo.
        echo ERROR: Could not install dependencies!
        echo.
        echo Try manually:
        echo   "%PY_EXE%" -m pip install -r requirements.txt
        echo.
        pause
        exit /b 1
    )
)
echo   OK: Dependencies ready

REM ─── Быстрая валидация таблицы ворот (не блокирует запуск) ───────────────
echo.
echo [3.5/4] Validating gate lookup table...
if exist "validate_lookup.py" (
    "%PY_EXE%" validate_lookup.py >nul 2>&1
    if errorlevel 1 (
        echo   WARNING: Gate lookup validation failed. Mapping issue still exists.
        echo   Check: fullhd_lookup.json ^(control points 24.4^>44, 11.5^>45^)
    ) else (
        echo   OK: Gate lookup validation passed
    )
) else (
    echo   WARNING: validate_lookup.py not found, skipping lookup validation
)

REM ─── Запуск PowerShell скрипта ─────────────────────────────────────────────
echo.
echo [4/4] Starting PowerShell launcher...
echo.

REM ЭТАП 2: исправить передачу пути
set "SCRIPT_PATH=%~dp0start_local_server.ps1"

REM ЭТАП 1: исправить кодировку запуска PowerShell
REM Используем -File для правильной передачи пути
powershell -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_PATH%" -PythonExe "%PY_EXE%"

REM После выхода
echo.
echo Servers stopped. Press Enter to exit...
pause


