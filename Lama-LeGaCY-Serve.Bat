:: Script: .\Llama-LeGaCY-Server.Bat

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

:: PYTHON READ BLOCK, DO NOT MODIFY: START:
if exist "%PERSISTENCE_FILE%" (
    echo Reading Python path from %PERSISTENCE_FILE%...
    set /p PYTHON_EXE_TO_USE=<%PERSISTENCE_FILE%
    if not exist "!PYTHON_EXE_TO_USE!" (
        echo Critical Error: `persistence.txt`.
        echo Run Setup-Install.Bat to Re-Configure.
        goto :end_of_script
    )
) else (
    echo File Missing: %PERSISTENCE_FILE%!
    echo Run Install-Setup.Bat First.
    goto :end_of_script
)
goto :start_display
:: PYTHON READ BLOCK, DO NOT MODIFY: END

:start_display
echo ================================================
echo              Llama-LeGaCY-Server
echo ================================================
echo.
echo Starting Llama-LeGaCY-Server...
timeout /t 1 >nul
echo Admin Status: Administrator
timeout /t 1 >nul
echo Script Path: %SCRIPT_DIRECTORY_PATH%
timeout /t 1 >nul
echo Python Path: %PYTHON_EXE_TO_USE%
timeout /t 1 >nul

:: Run the Python server script
echo Running `llama_legacy_serve.py`...
!PYTHON_EXE_TO_USE! llama_legacy_serve.py
if errorlevel 1 (
    echo Error: Failed to start LLaMa-LeGaCY-SerVer.
)
echo ...`llama_legacy_serve.py` Exited.

:end_of_script
echo All Processes Finished
timeout /t 5 >nul
endlocal
exit /b 0
