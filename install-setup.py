# Script: .\install_setup.py

# Imports
import os, sys, subprocess, requests, 
import yaml, json, logging, zipfile
from typing import List, Dict, Union

# Global variables
DATA_FOLDER = ".\\data"
PERSISTENCE_YAML = os.path.join(DATA_FOLDER, "persistence.yaml")
LLAMA_BIN_DIR = os.path.join(DATA_FOLDER, "llama-binaries")
GITHUB_BASE_URL = "https://github.com/ggerganov/llama.cpp/releases/download/"

# Set up logging
logging.basicConfig(filename='setup.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def get_gpu_info() -> List[Dict[str, Union[str, float]]]:
    try:
        import wmi
        c = wmi.WMI()
        gpus = []
        for gpu in c.Win32_VideoController():
            gpus.append({
                'name': gpu.Name,
                'vram': float(gpu.AdapterRAM) / (1024 * 1024) if gpu.AdapterRAM else 0
            })
        return gpus
    except Exception as e:
        logging.error(f"Error getting GPU info: {e}")
        return []

def get_cpu_info() -> Dict[str, Union[str, int]]:
    try:
        import cpuinfo
        info = cpuinfo.get_cpu_info()
        return {
            'name': info['brand_raw'],
            'cores': info['count'],
            'threads': info['count'],
            'flags': info['flags']
        }
    except Exception as e:
        logging.error(f"Error getting CPU info: {e}")
        return {}

def get_ram_info() -> float:
    try:
        import psutil
        return psutil.virtual_memory().total / (1024 * 1024)  # Convert to MB
    except Exception as e:
        logging.error(f"Error getting RAM info: {e}")
        return 0

def determine_compatible_binaries(gpu_info: List[Dict[str, Union[str, float]]], cpu_info: Dict[str, Union[str, int]]) -> List[str]:
    compatible_binaries = []
    
    # CPU binaries
    if 'avx512' in cpu_info['flags']:
        compatible_binaries.append("llama-b3672-bin-win-avx512-x64.zip")
    if 'avx2' in cpu_info['flags']:
        compatible_binaries.append("llama-b3672-bin-win-avx2-x64.zip")
    if 'avx' in cpu_info['flags']:
        compatible_binaries.append("llama-b3672-bin-win-avx-x64.zip")
    compatible_binaries.append("llama-b3672-bin-win-noavx-x64.zip")
    
    # OpenBLAS binary (useful for all CPU types)
    compatible_binaries.append("llama-b3672-bin-win-openblas-x64.zip")
    
    # Check for NVIDIA GPUs
    if any('nvidia' in gpu['name'].lower() for gpu in gpu_info):
        compatible_binaries.extend([
            "cudart-llama-bin-win-cu11.7.1-x64.zip",
            "cudart-llama-bin-win-cu12.2.0-x64.zip",
            "llama-b3672-bin-win-cuda-cu11.7.1-x64.zip",
            "llama-b3672-bin-win-cuda-cu12.2.0-x64.zip"
        ])
    
    # Check for AMD GPUs
    if any('amd' in gpu['name'].lower() for gpu in gpu_info):
        compatible_binaries.extend([
            "llama-b3672-bin-win-vulkan-x64.zip",
            "llama-b3085-bin-win-clblast-x64.zip"  # OpenCL support for older AMD cards
        ])
    
    # Check for Intel GPUs
    if any('intel' in gpu['name'].lower() for gpu in gpu_info):
        compatible_binaries.append("llama-b3672-bin-win-vulkan-x64.zip")  # Vulkan support for Intel GPUs
    
    # Add SYCL binary (for Intel GPUs and some AMD GPUs)
    compatible_binaries.append("llama-b3672-bin-win-sycl-x64.zip")
    
    # Add Kompute binary (for various GPUs, including mobile)
    compatible_binaries.append("llama-b3672-bin-win-kompute-x64.zip")
    
    # Add ARM64 binaries if running on ARM
    if 'arm' in cpu_info['flags']:
        compatible_binaries.extend([
            "llama-b3672-bin-win-llvm-arm64.zip",
            "llama-b3672-bin-win-msvc-arm64.zip"
        ])
    
    return list(set(compatible_binaries))  # Remove duplicates

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

def update_persistence_file(persistence_data: Dict[str, Union[str, int, float, List, Dict]]):
    with open(PERSISTENCE_YAML, 'w') as f:
        yaml.dump(persistence_data, f)

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
        if binary_type == 'cpu' and not any(x in binary.lower() for x in ['cuda', 'vulkan', 'clblast', 'sycl', 'kompute']):
            download_and_extract(f"{GITHUB_BASE_URL}b3672/{binary}", LLAMA_BIN_DIR)
        elif binary_type == 'gpu' and any(x in binary.lower() for x in ['cuda', 'vulkan', 'clblast', 'sycl', 'kompute']):
            if 'clblast' in binary.lower():
                download_and_extract(f"{GITHUB_BASE_URL}b3085/{binary}", LLAMA_BIN_DIR)
            else:
                download_and_extract(f"{GITHUB_BASE_URL}b3672/{binary}", LLAMA_BIN_DIR)


def main():
    try:
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

        # Update persistence file
        persistence_data = {
            'GPU_TYPE': [],
            'THREADS': cpu_info['threads'],
            'RAM_CAPACITY': ram_capacity,
            'VRAM_CAPACITY': {}
        }
        
        for gpu in gpu_info:
            if 'nvidia' in gpu['name'].lower():
                persistence_data['GPU_TYPE'].append('NVIDIA')
            elif 'amd' in gpu['name'].lower():
                persistence_data['GPU_TYPE'].append('AMD')
            elif 'intel' in gpu['name'].lower():
                persistence_data['GPU_TYPE'].append('Intel')
            else:
                persistence_data['GPU_TYPE'].append('Unknown')
            
            persistence_data['VRAM_CAPACITY'][gpu['name']] = gpu['vram']
        
        update_persistence_file(persistence_data)

        # Menu loop
        while True:
            print("\n===== LMS-Local Setup Menu =====")
            print("1. Install Python Libraries")
            print("2. Install CPU Binaries")
            print("3. Install GPU Binaries")
            print("4. Install Both CPU and GPU Binaries")
            print("5. Display Hardware Info")
            print("6. Exit")
            choice = input("Enter your choice (1-6): ")

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
                with open(os.path.join(DATA_FOLDER, 'hardware_info.txt'), 'r') as f:
                    print(f.read())
            elif choice == '6':
                print("Exiting setup...")
                break
            else:
                print("Invalid choice. Please try again.")

    except Exception as e:
        logging.error(f"An error occurred during setup: {e}")
        print(f"An error occurred. Please check the setup.log file for details.")

if __name__ == "__main__":
    main()