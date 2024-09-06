@echo off
setlocal EnableDelayedExpansion

:: Global Variables
set "PIP_EXE_TO_USE="
set "PYTHON_EXE_TO_USE="
set PERSISTENCE_TXT=.\data\persistence.txt
set PERSISTENCE_YAML=.\data\persistence.yaml
set DATA_FOLDER=.\data
set LLAMA_BIN_DIR=%DATA_FOLDER%\llama-binaries

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
    goto :eof
)
echo Python Found: %PYTHON_EXE_TO_USE%
timeout /t 1 >nul

:: Create the data folder if it doesn't exist
if not exist %DATA_FOLDER% mkdir %DATA_FOLDER%
if not exist %LLAMA_BIN_DIR% mkdir %LLAMA_BIN_DIR%

:: Create persistence.txt if it doesn't exist
if not exist %PERSISTENCE_TXT% (
    echo Creating %PERSISTENCE_TXT%...
    echo GPU_TYPE=CPU> %PERSISTENCE_TXT%
    echo THREADS=4>> %PERSISTENCE_TXT%
    echo LAYERS=All>> %PERSISTENCE_TXT%
    echo MODEL_DIR=.\models>> %PERSISTENCE_TXT%
    echo PYTHON_EXE=%PYTHON_EXE_TO_USE%>> %PERSISTENCE_TXT%
)

:: Create persistence.yaml if it doesn't exist (but don't use it)
if not exist %PERSISTENCE_YAML% (
    echo Creating %PERSISTENCE_YAML%...
    echo # LMS-Local Persistence File > %PERSISTENCE_YAML%
    echo GPU_TYPE: CPU >> %PERSISTENCE_YAML%
    echo THREADS: 4 >> %PERSISTENCE_YAML%
    echo LAYERS: All >> %PERSISTENCE_YAML%
    echo MODEL_DIR: .\models >> %PERSISTENCE_YAML%
    echo PYTHON_EXE: %PYTHON_EXE_TO_USE% >> %PERSISTENCE_YAML%
)

:: Hardware detection: NVIDIA, AMD, or CPU
echo Detecting hardware...
wmic path win32_VideoController get name > %DATA_FOLDER%\hardware.txt
findstr /C:"NVIDIA" %DATA_FOLDER%\hardware.txt > nul && (
    echo NVIDIA GPU detected.
    echo Updating GPU_TYPE in persistence.txt...
    powershell -Command "(Get-Content %PERSISTENCE_TXT%) -replace 'GPU_TYPE=.*', 'GPU_TYPE=NVIDIA' | Set-Content %PERSISTENCE_TXT%"
)
findstr /C:"AMD" %DATA_FOLDER%\hardware.txt > nul && (
    echo AMD GPU detected.
    echo Updating GPU_TYPE in persistence.txt...
    powershell -Command "(Get-Content %PERSISTENCE_TXT%) -replace 'GPU_TYPE=.*', 'GPU_TYPE=AMD' | Set-Content %PERSISTENCE_TXT%"
)

:: Main Menu
:main_menu
cls
echo ================================================
echo                  Setup-Installer
echo ================================================
echo 1. Install Python Libraries
echo 2. Llama Binaries Installer
echo ------------------------------------------------
echo.
set /p "choice=Selection; Menu Options = 1-2, Save and Exit = X: "

if "%choice%"=="1" goto install_python_libraries
if "%choice%"=="2" goto llama_binaries_menu
if /i "%choice%"=="X" goto save_and_exit
goto main_menu

:install_python_libraries
echo Installing Python libraries...
%PYTHON_EXE_TO_USE% -m pip install -r requirements.txt
echo Checking for dependency issues...
%PYTHON_EXE_TO_USE% -m pip check
pause
goto main_menu

:llama_binaries_menu
cls
echo ================================================
echo              llaMa-LeGaCY-SerVer
echo ================================================
echo 1. Install Compatible CPU Binaries
echo 2. Install Compatible GPU Binaries
echo 3. Install Both Sets Of Binaries
echo ------------------------------------------------
echo Detected CPUs:
wmic cpu get name
echo Total Threads:
wmic cpu get NumberOfLogicalProcessors
echo Detected GPUs:
wmic path win32_VideoController get name
echo.
echo Required CPPs:
echo cudart-llama-bin-win-cu11.7.1-x64.zip - 293MB
echo cudart-llama-bin-win-cu12.2.0-x64.zip - 413MB
echo llama-b3672-bin-macos-arm64.zip - 50MB
echo llama-b3672-bin-macos-x64.zip - 51.8MB
echo llama-b3672-bin-ubuntu-x64.zip - 55.6MB
echo llama-b3672-bin-win-avx-x64.zip - 7.76MB
echo llama-b3672-bin-win-avx2-x64.zip - 7.76MB
echo llama-b3672-bin-win-avx512-x64.zip - 7.76MB
echo llama-b3672-bin-win-cuda-cu11.7.1-x64.zip - 145MB
echo llama-b3672-bin-win-cuda-cu12.2.0-x64.zip - 144MB
echo llama-b3672-bin-win-kompute-x64.zip - 8.04MB
echo llama-b3672-bin-win-llvm-arm64.zip - 11.4MB
echo llama-b3672-bin-win-msvc-arm64.zip - 13.4MB
echo llama-b3672-bin-win-noavx-x64.zip - 7.74MB
echo llama-b3672-bin-win-openblas-x64.zip - 18.8MB
echo llama-b3672-bin-win-sycl-x64.zip - 69.3MB
echo llama-b3672-bin-win-vulkan-x64.zip - 8.37MB
echo ================================================
set /p "binary_choice=Selection; Menu Options = 1-3, Back to Main Menu = B: "

if "%binary_choice%"=="1" goto install_cpu_binaries
if "%binary_choice%"=="2" goto install_gpu_binaries
if "%binary_choice%"=="3" goto install_both_binaries
if /i "%binary_choice%"=="B" goto main_menu
goto llama_binaries_menu

:install_cpu_binaries
echo Installing CPU binaries...
powershell -Command "Invoke-WebRequest -Uri 'https://github.com/ggerganov/llama.cpp/releases/download/b3672/llama-b3672-bin-win-avx2-x64.zip' -OutFile '%LLAMA_BIN_DIR%\cpu_binaries.zip'"
powershell -Command "Expand-Archive -Path '%LLAMA_BIN_DIR%\cpu_binaries.zip' -DestinationPath '%LLAMA_BIN_DIR%\cpu' -Force"
echo CPU binaries installed.
pause
goto llama_binaries_menu

:install_gpu_binaries
echo Installing GPU binaries...
for /f "tokens=2 delims==" %%a in ('type %PERSISTENCE_TXT% ^| findstr "GPU_TYPE"') do set GPU_TYPE=%%a
if "%GPU_TYPE%"=="NVIDIA" (
    set /p CUDA_VER="Enter your CUDA version (e.g., 11.7 or 12.2): "
    if "%CUDA_VER%"=="11.7" (
        powershell -Command "Invoke-WebRequest -Uri 'https://github.com/ggerganov/llama.cpp/releases/download/b3672/cudart-llama-bin-win-cu11.7.1-x64.zip' -OutFile '%LLAMA_BIN_DIR%\gpu_binaries.zip'"
    ) else if "%CUDA_VER%"=="12.2" (
        powershell -Command "Invoke-WebRequest -Uri 'https://github.com/ggerganov/llama.cpp/releases/download/b3672/cudart-llama-bin-win-cu12.2.0-x64.zip' -OutFile '%LLAMA_BIN_DIR%\gpu_binaries.zip'"
    ) else (
        echo Unsupported CUDA version!
        pause
        goto llama_binaries_menu
    )
) else if "%GPU_TYPE%"=="AMD" (
    echo AMD GPU support is not yet implemented.
    pause
    goto llama_binaries_menu
) else (
    echo No compatible GPU detected.
    pause
    goto llama_binaries_menu
)
powershell -Command "Expand-Archive -Path '%LLAMA_BIN_DIR%\gpu_binaries.zip' -DestinationPath '%LLAMA_BIN_DIR%\gpu' -Force"
echo GPU binaries installed.
pause
goto llama_binaries_menu

:install_both_binaries
call :install_cpu_binaries
call :install_gpu_binaries
goto llama_binaries_menu

:save_and_exit
echo Saving configuration...
powershell -Command "(Get-Content %PERSISTENCE_TXT%) -replace 'PYTHON_EXE=.*', 'PYTHON_EXE=%PYTHON_EXE_TO_USE%' | Set-Content %PERSISTENCE_TXT%"
echo Configuration saved. Exiting...
exit /b 0