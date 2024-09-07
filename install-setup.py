import os
import sys
import subprocess
import json
import yaml
import requests
import zipfile
from typing import List, Dict

# Global variables
DATA_FOLDER = ".\\data"
PERSISTENCE_TXT = os.path.join(DATA_FOLDER, "persistence.txt")
PERSISTENCE_YAML = os.path.join(DATA_FOLDER, "persistence.yaml")
LLAMA_BIN_DIR = os.path.join(DATA_FOLDER, "llama-binaries")
GITHUB_BASE_URL = "https://github.com/ggerganov/llama.cpp/releases/download/"

def get_gpu_info() -> List[Dict[str, Union[str, float]]]:
    try:
        result = subprocess.run(['wmic', 'path', 'win32_VideoController', 'get', 'name,AdapterRAM', '/format:list'], capture_output=True, text=True)
        gpu_info = result.stdout.strip().split('\n')
        gpus = []
        current_gpu = {}
        for line in gpu_info:
            if line.startswith('AdapterRAM='):
                current_gpu['vram'] = int(line.split('=')[1]) / (1024 * 1024)  # Convert to MB
            elif line.startswith('Name='):
                if current_gpu:
                    gpus.append(current_gpu)
                current_gpu = {'name': line.split('=')[1]}
        if current_gpu:
            gpus.append(current_gpu)
        return gpus
    except Exception as e:
        print(f"Error getting GPU info: {e}")
        return []

def get_cpu_info() -> Dict[str, Union[str, int]]:
    try:
        result = subprocess.run(['wmic', 'cpu', 'get', 'name,numberofcores,numberoflogicalprocessors', '/format:list'], capture_output=True, text=True)
        cpu_info = result.stdout.strip().split('\n')
        cpu = {}
        for line in cpu_info:
            if line.startswith('Name='):
                cpu['name'] = line.split('=')[1]
            elif line.startswith('NumberOfCores='):
                cpu['cores'] = int(line.split('=')[1])
            elif line.startswith('NumberOfLogicalProcessors='):
                cpu['threads'] = int(line.split('=')[1])
        return cpu
    except Exception as e:
        print(f"Error getting CPU info: {e}")
        return {}

def get_ram_info() -> float:
    try:
        result = subprocess.run(['wmic', 'computersystem', 'get', 'totalphysicalmemory', '/format:list'], capture_output=True, text=True)
        ram_info = result.stdout.strip().split('\n')
        for line in ram_info:
            if line.startswith('TotalPhysicalMemory='):
                return int(line.split('=')[1]) / (1024 * 1024)  # Convert to MB
    except Exception as e:
        print(f"Error getting RAM info: {e}")
        return 0

def determine_compatible_binaries(gpu_info: List[Dict[str, Union[str, float]]], cpu_info: Dict[str, Union[str, int]]) -> List[str]:
    compatible_binaries = []
    
    # CPU binaries
    compatible_binaries.append("llama-b3672-bin-win-avx2-x64.zip")
    compatible_binaries.append("llama-b3672-bin-win-avx-x64.zip")
    
    # Check for NVIDIA GPUs
    if any('nvidia' in gpu['name'].lower() for gpu in gpu_info):
        compatible_binaries.append("cudart-llama-bin-win-cu11.7.1-x64.zip")
        compatible_binaries.append("cudart-llama-bin-win-cu12.2.0-x64.zip")
    
    # Check for AMD GPUs
    if any('amd' in gpu['name'].lower() for gpu in gpu_info):
        compatible_binaries.append("llama-b3672-bin-win-vulkan-x64.zip")
        compatible_binaries.append("llama-b3085-bin-win-clblast-x64.zip")  # OpenCL support for older AMD cards
    
    return compatible_binaries

def save_hardware_info(cpu_info: Dict[str, Union[str, int]], ram_capacity: float, gpu_info: List[Dict[str, Union[str, float]]]):
    with open(os.path.join(DATA_FOLDER, 'hardware_info.txt'), 'w') as f:
        f.write(f"CPU: {cpu_info['name']} ({cpu_info['cores']} cores, {cpu_info['threads']} threads)\n")
        f.write(f"RAM: {ram_capacity:.2f} MB\n")
        for idx, gpu in enumerate(gpu_info, 1):
            f.write(f"GPU {idx}: {gpu['name']} (VRAM: {gpu['vram']:.2f} MB)\n")

def save_compatible_binaries(compatible_binaries: List[str]):
    with open(os.path.join(DATA_FOLDER, 'compatible_binaries.txt'), 'w') as f:
        for binary in compatible_binaries:
            f.write(f"{binary}\n")

def update_persistence_files(persistence_data: Dict[str, Union[str, int, float]]):
    # Update TXT file
    with open(PERSISTENCE_TXT, 'r') as f:
        lines = f.readlines()
    
    with open(PERSISTENCE_TXT, 'w') as f:
        for line in lines:
            key = line.split('=')[0]
            if key in persistence_data:
                f.write(f"{key}={persistence_data[key]}\n")
            else:
                f.write(line)
    
    # Update YAML file
    with open(PERSISTENCE_YAML, 'r') as f:
        yaml_data = yaml.safe_load(f)
    
    yaml_data.update(persistence_data)
    
    with open(PERSISTENCE_YAML, 'w') as f:
        yaml.dump(yaml_data, f)

def download_and_extract(url: str, target_dir: str):
    response = requests.get(url)
    if response.status_code == 200:
        zip_path = os.path.join(target_dir, "temp.zip")
        with open(zip_path, 'wb') as f:
            f.write(response.content)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(target_dir)
        
        os.remove(zip_path)
        print(f"Successfully installed: {os.path.basename(url)}")
    else:
        print(f"Failed to download: {url}")

def install_binaries(binary_type: str):
    with open(os.path.join(DATA_FOLDER, 'compatible_binaries.txt'), 'r') as f:
        compatible_binaries = f.read().splitlines()
    
    for binary in compatible_binaries:
        if binary_type == 'cpu' and 'cuda' not in binary.lower() and 'vulkan' not in binary.lower() and 'clblast' not in binary.lower():
            download_and_extract(f"{GITHUB_BASE_URL}b3672/{binary}", LLAMA_BIN_DIR)
        elif binary_type == 'gpu' and ('cuda' in binary.lower() or 'vulkan' in binary.lower() or 'clblast' in binary.lower()):
            if 'clblast' in binary.lower():
                download_and_extract(f"{GITHUB_BASE_URL}b3085/{binary}", LLAMA_BIN_DIR)
            else:
                download_and_extract(f"{GITHUB_BASE_URL}b3672/{binary}", LLAMA_BIN_DIR)

def main():
    # Create necessary directories
    os.makedirs(DATA_FOLDER, exist_ok=True)
    os.makedirs(LLAMA_BIN_DIR, exist_ok=True)

    # Detect hardware
    gpu_info = get_gpu_info()
    cpu_info = get_cpu_info()
    ram_capacity = get_ram_info()

    # Save hardware info
    save_hardware_info(cpu_info, ram_capacity, gpu_info)

    # Determine compatible binaries
    compatible_binaries = determine_compatible_binaries(gpu_info, cpu_info)
    save_compatible_binaries(compatible_binaries)

    # Update persistence files
    persistence_data = {
        'GPU_TYPE': 'NVIDIA' if any('nvidia' in gpu['name'].lower() for gpu in gpu_info) else 'AMD' if any('amd' in gpu['name'].lower() for gpu in gpu_info) else 'CPU',
        'THREADS': cpu_info['threads'],
        'RAM_CAPACITY': ram_capacity,
        'VRAM_CAPACITY': sum(gpu['vram'] for gpu in gpu_info)
    }
    update_persistence_files(persistence_data)

    # Menu loop
    while True:
        print("\n===== LMS-Local Setup Menu =====")
        print("1. Install Python Libraries")
        print("2. Install CPU Binaries")
        print("3. Install GPU Binaries")
        print("4. Install Both CPU and GPU Binaries")
        print("5. Exit")
        choice = input("Enter your choice (1-5): ")

        if choice == '1':
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            subprocess.run([sys.executable, "-m", "pip", "check"])
        elif choice == '2':
            install_binaries('cpu')
        elif choice == '3':
            install_binaries('gpu')
        elif choice == '4':
            install_binaries('cpu')
            install_binaries('gpu')
        elif choice == '5':
            print("Exiting setup...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()