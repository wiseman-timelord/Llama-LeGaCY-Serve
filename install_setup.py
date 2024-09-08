import os
import subprocess
import logging
import sys
import torch
import cpuinfo
import requests
import zipfile
import json
from tqdm import tqdm

# Global variables
DATA_FOLDER = ".\\data"
PERSISTENCE_TXT = os.path.join(DATA_FOLDER, "persistence.txt")
PERSISTENCE_JSON = os.path.join(DATA_FOLDER, "persistence.json")
PYTHON_EXE_TO_USE = None
BINARIES_FOLDER = ".\\binaries"
GITHUB_RELEASE_URL = "https://github.com/ggerganov/llama.cpp/releases/download/b3680/"

logging.basicConfig(filename='install_setup.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_script_header():
    clear_screen()
    print("=" * 120)
    print("    Llama-Legacy-Serve Install-Setup")
    print("=" * 120)
    print("\n")

def read_python_exe_from_persistence():
    global PYTHON_EXE_TO_USE
    try:
        if os.path.exists(PERSISTENCE_TXT):
            with open(PERSISTENCE_TXT, "r") as file:
                PYTHON_EXE_TO_USE = file.readline().strip()
            if not os.path.exists(PYTHON_EXE_TO_USE):
                raise FileNotFoundError(f"Python executable not found: {PYTHON_EXE_TO_USE}")
        else:
            raise FileNotFoundError(f"persistence.txt not found at {PERSISTENCE_TXT}")
    except Exception as e:
        logging.error(f"Error reading Python executable: {str(e)}")
        print(f"Error: {str(e)}")
        sys.exit(1)

def install_python_libraries():
    print_script_header()
    print("Installing Python Libraries...\n")
    requirements_main = os.path.join(DATA_FOLDER, 'requirements_main.txt')
    try:
        if os.path.exists(requirements_main):
            subprocess.run([PYTHON_EXE_TO_USE, "-m", "pip", "install", "-r", requirements_main], check=True)
            subprocess.run([PYTHON_EXE_TO_USE, "-m", "pip", "check"], check=True)
            print(f"Installed Python libraries from {requirements_main}")
            logging.info(f"Successfully installed Python libraries from {requirements_main}")
        else:
            raise FileNotFoundError(f"Requirements file not found: {requirements_main}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error installing Python libraries: {str(e)}")
        print(f"Error: Failed to install Python libraries. Check the log for details.")
    except Exception as e:
        logging.error(f"Unexpected error during library installation: {str(e)}")
        print(f"Unexpected error: {str(e)}")

def detect_hardware():
    print("Detecting hardware...")
    cpu_info = cpuinfo.get_cpu_info()
    
    cpu_type = "noavx"
    if cpu_info['flags'].get('avx512f'):
        cpu_type = "avx512"
    elif cpu_info['flags'].get('avx2'):
        cpu_type = "avx2"
    elif cpu_info['flags'].get('avx'):
        cpu_type = "avx"

    print(f"CPU: {cpu_info['brand_raw']} ({cpu_type})")
    
    gpus = []
    if torch.cuda.is_available():
        cuda_version = torch.version.cuda
        for i in range(torch.cuda.device_count()):
            gpu_name = torch.cuda.get_device_name(i)
            print(f"GPU {i}: {gpu_name}")
            gpus.append({"index": i, "name": gpu_name, "cuda_version": cuda_version})
    else:
        print("No CUDA-capable GPUs detected")

    hardware_info = {
        "cpu": {
            "brand": cpu_info['brand_raw'],
            "type": cpu_type
        },
        "gpus": gpus
    }
    
    logging.info(f"Detected hardware: {json.dumps(hardware_info)}")
    return hardware_info

def download_file(url, filename):
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    with open(filename, "wb") as file, tqdm(
        desc=filename,
        total=total_size,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as progress_bar:
        for data in response.iter_content(chunk_size=1024):
            size = file.write(data)
            progress_bar.update(size)

def install_binaries(hardware_info):
    print("Installing binaries...")
    os.makedirs(BINARIES_FOLDER, exist_ok=True)

    binaries_to_install = set()

    # CPU binary
    cpu_binary = f"llama-b3672-bin-win-{hardware_info['cpu']['type']}-x64.zip"
    binaries_to_install.add(cpu_binary)

    # GPU binaries
    for gpu in hardware_info['gpus']:
        cuda_version = gpu['cuda_version']
        if cuda_version.startswith("11"):
            binaries_to_install.add("llama-b3672-bin-win-cuda-cu11.7.1-x64.zip")
        elif cuda_version.startswith("12"):
            binaries_to_install.add("llama-b3672-bin-win-cuda-cu12.2.0-x64.zip")

    for binary_zip in binaries_to_install:
        binary_url = GITHUB_RELEASE_URL + binary_zip
        zip_path = os.path.join(BINARIES_FOLDER, binary_zip)

        print(f"Downloading {binary_zip}...")
        download_file(binary_url, zip_path)

        print(f"Extracting {binary_zip}...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(BINARIES_FOLDER)

        os.remove(zip_path)
        print(f"Installed binary: {binary_zip}")
        logging.info(f"Installed binary: {binary_zip}")

    hardware_info['installed_binaries'] = list(binaries_to_install)
    return hardware_info

def save_hardware_info(hardware_info):
    with open(PERSISTENCE_JSON, 'w') as f:
        json.dump(hardware_info, f, indent=2)
    print(f"Hardware information saved to {PERSISTENCE_JSON}")
    logging.info(f"Hardware information saved to {PERSISTENCE_JSON}")

def detect_and_install_binaries():
    print_script_header()
    print("Detecting Hardware and Installing Binaries...\n")
    hardware_info = detect_hardware()
    hardware_info = install_binaries(hardware_info)
    save_hardware_info(hardware_info)

def main_menu():
    while True:
        print_script_header()
        print("    1. Install Python Libraries")
        print('    (./data/requirements_main.txt)\n')
        print("    2. Detect Hardware and Install Binaries\n\n")
        print("-" * 120)
        print("")
        print("Python Path:")
        print(f"{PYTHON_EXE_TO_USE}")
        print("")
        print("=" * 120)
        choice = input("Selection; Menu Options = 1-2, Exit Setup-Install = X: ").strip().lower()

        if choice == '1':
            install_python_libraries()
        elif choice == '2':
            detect_and_install_binaries()
        elif choice == 'x':
            print("Exiting setup...")
            logging.info("User exited the setup")
            break
        else:
            print("Invalid choice. Please try again.")
        
        input("Press Enter to continue...")

def main():
    try:
        read_python_exe_from_persistence()
        logging.info(f"Setup started with Python executable: {PYTHON_EXE_TO_USE}")
        main_menu()
    except Exception as e:
        logging.error(f"Unhandled exception in main: {str(e)}")
        print(f"An unexpected error occurred: {str(e)}")
        print("Please check the log file for more details.")

if __name__ == "__main__":
    main()