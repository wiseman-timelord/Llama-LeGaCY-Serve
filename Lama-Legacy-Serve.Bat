:: SCRIPT: Llama-LeGaCY-Server.Bat
@echo off

:: Global Variables
set "PIP_EXE_TO_USE="
set "PYTHON_EXE_TO_USE="

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

echo ================================================
echo              LLaMa-LeGaCY-SerVer
echo ================================================

echo Starting LMS-Local...
%PYTHON_EXE_TO_USE% lms_local.py
pause
