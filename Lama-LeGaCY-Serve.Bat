:: SCRIPT: Llama-LeGaCY-Server.Bat

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

:: PYTHON READ BLOCK, DO NOT MODIFY: START:
if exist ".\data\persistence.txt" (
    set /p PYTHON_EXE_TO_USE=<.\data\persistence.txt
    if not exist "!PYTHON_EXE_TO_USE!" (
        echo Critical Error: `persistence.txt` corrupt.
        imeout /t 3 >nul
		goto :end_of_script
    )
) else (
    echo File Missing: .\data\persistence.txt!
    echo Run Install-Setup.Bat First.
	timeout /t 3 >nul
	goto :end_of_script
)
:: PYTHON READ BLOCK, DO NOT MODIFY: START:

:: Start Display
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
timeout /t 2 >nul
goto :end_of_script

:end_of_script
echo All Processes Finished
timeout /t 5 >nul
endlocal
exit /b 0
