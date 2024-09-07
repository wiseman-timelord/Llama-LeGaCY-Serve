:: Script: .\Install-Setup.Bat - the launcher for install_setup.py

:: Initialization
@echo off
setlocal EnableDelayedExpansion

:: Globals
set "PYTHON_EXE_TO_USE="
set "SCRIPT_DIRECTORY_PATH=%~dp0"
set "PERSISTENCE_FILE=.\data\persistence.txt"

:: ADMIN AND DP0, BLOCK, DO NOT MODIFY: START
net session >nul 2>&1 || (
    echo Error: Admin privileges required.
    echo Right-click and select "Run as administrator".
    goto :end_of_script
)
pushd "%SCRIPT_DIRECTORY_PATH%"
:: ADMIN AND DP0, BLOCK, DO NOT MODIFY: END

:: PYTHON READ BLOCK, DO NOT MODIFY: START
if not exist "%PERSISTENCE_FILE%" (
    echo File Missing: %PERSISTENCE_FILE%!
    echo Detecting Python Location.
    goto :find_python
)
echo Checking File: %PERSISTENCE_FILE%
set /p PYTHON_EXE_TO_USE=<%PERSISTENCE_FILE%
if not exist "!PYTHON_EXE_TO_USE!" (
    echo Invalid Python path in %PERSISTENCE_FILE%.
    echo Re-detecting Python Location.
    goto :find_python
)
echo Valid Python found: !PYTHON_EXE_TO_USE!
goto :start_display
:find_python
for %%I in (
    "C:\Program Files\Python312\python.exe"
    "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312\python.exe"
) do if exist "%%~I" (
    set "PYTHON_EXE_TO_USE=%%~I"
    echo File Saved %PERSISTENCE_FILE%.
    goto :start_display
)
echo Error: Python 3.12 not found.
goto :end_of_script
:: PYTHON READ BLOCK, DO NOT MODIFY: END

:start_display
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
echo Running `install_setup.py`...
!PYTHON_EXE_TO_USE! install_setup.py
echo ...`install_setup.py` Exited.

:end_of_script
echo All Processes Finished
pause >nul
endlocal
exit /b 0
