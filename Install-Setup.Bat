:: Script: .\Install-Setup.Bat

:: Initialization
@echo off
setlocal EnableDelayedExpansion

:: Globals
set "PYTHON_EXE_TO_USE="
set "SCRIPT_DIRECTORY_PATH="

:: ADMIN AND DP0, BLOCK, DO NOT MODIFY: START
net session >nul 2>&1 || (
    echo Error: Admin privileges required. Right-click and select "Run as administrator".
    timeout /t 3 >nul
    goto :end_of_script
)
set "SCRIPT_DIRECTORY_PATH=%~dp0"
set "SCRIPT_DIRECTORY_PATH=%SCRIPT_DIRECTORY_PATH:~0,-1%"
pushd "%SCRIPT_DIRECTORY_PATH%"
:: ...ADMIN AND DP0, BLOCK, DO NOT MODIFY: END

:: PYTHON FIND BLOCK, DO NOT MODIFY: START
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
    goto :end_of_script
)
:: PYTHON FIND BLOCK, DO NOT MODIFY: END

:: Start Display
cls
echo ================================================
echo                  Install-Setup
echo ================================================
echo.
echo Starting Setup-Install...
timeout /t 1 >nul
echo Admin Status: Administrator
timeout /t 1 >nul
echo Script Path: %SCRIPT_DIRECTORY_PATH%
timeout /t 1 >nul
echo Python Path: %PYTHON_EXE_TO_USE%
timeout /t 1 >nul

:: Run the Python setup script
echo Running `install_setup.py.py`...
%PYTHON_EXE_TO_USE% install_setup.py
echo ...`install_setup.py` Exited.
goto :end_of_script

:end_of_script
echo All Processes Finished
pause >nul
endlocal
exit /b 0