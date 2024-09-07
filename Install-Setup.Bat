:: Script: .\Install-Setup.Bat
@echo off
setlocal EnableDelayedExpansion

:: ADMIN AND DP0, BLOCK, DO NOT MODIFY: START
net session >nul 2>&1 || (
    echo Error: Admin privileges required. Right-click and select "Run as administrator".
    timeout /t 3 >nul
    exit /b 1
)
echo Status: Administrator
timeout /t 1 >nul
set "SCRIPT_DIRECTORY_PATH=%~dp0"
set "SCRIPT_DIRECTORY_PATH=%SCRIPT_DIRECTORY_PATH:~0,-1%"
pushd "%SCRIPT_DIRECTORY_PATH%"
echo Path Dp0'd To Script.
timeout /t 1 >nul
:: ...ADMIN AND DP0, BLOCK, DO NOT MODIFY: END

:: Find Python 3.12
for %%I in (
    "C:\Program Files\Python312\python.exe"
    "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312\python.exe"
) do (
    if exist "%%~I" (
        set "PYTHON_EXE_TO_USE=%%~I"
        goto :found_python312
    )
)
:found_python312
if not defined PYTHON_EXE_TO_USE (
    echo Error: Python 3.12 not found. Please install it before running this script.
    timeout /t 3 >nul
    exit /b 1
)
echo Python Found: %PYTHON_EXE_TO_USE%
timeout /t 1 >nul

:: Run the Python setup script
%PYTHON_EXE_TO_USE% install_setup.py

echo Setup complete. Press any key to exit...
pause >nul
exit /b 0