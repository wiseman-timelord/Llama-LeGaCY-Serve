# Script: .\install_setup.py

# Imports
import os, subprocess, psutil, json, logging, zipfile, wmi
from typing import List, Dict, Union

# Global variables
DATA_FOLDER = ".\\data"
LLAMA_BIN_DIR = os.path.join(DATA_FOLDER, "llama-binaries")
GITHUB_BASE_URL = "https://github.com/ggerganov/llama.cpp/releases/download/"
PERSISTENCE_JSON = os.path.join(DATA_FOLDER, "persistence.json")

# Set up logging
logging.basicConfig(filename='setup.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def get_gpu_info():
    """Fetch GPU information using WMI."""
    try:
        c = wmi.WMI()
        gpus = []
        for gpu in c.Win32_VideoController():
            gpus.append({
                'graphics_brand': gpu.AdapterCompatibility,
                'graphics_name': gpu.Name,
                'graphics_total_shaders': gpu.AdapterDACType,  # Placeholder for shaders, actual may require another query
                'graphics_total_vram': float(gpu.AdapterRAM) / (1024 * 1024)  # Convert to MB
            })
        return gpus
    except Exception as e:
        logging.error(f"Error fetching GPU info: {e}")
        return []

def get_cpu_info():
    """Fetch CPU core and thread information."""
    try:
        cpu_info = {
            'processor_brand': psutil.cpu_info().brand_raw if hasattr(psutil, 'cpu_info') else "Unknown",
            'processor_name': os.popen("wmic cpu get Name").read().split('\n')[1].strip(),
            'processor_total_threads': psutil.cpu_count(logical=True),
            'processor_total_ram': psutil.virtual_memory().total / (1024 * 1024)  # Convert to MB
        }
        return cpu_info
    except Exception as e:
        logging.error(f"Error fetching CPU info: {e}")
        return {}

def save_to_persistence_json(gpu_info: List[Dict[str, Union[str, float]]], cpu_info: Dict[str, Union[str, int]]):
    """Save GPU, CPU, and available binaries info to persistence.json."""
    persistence_data = {}

    # If persistence.json exists, load its content
    if os.path.exists(PERSISTENCE_JSON):
        with open(PERSISTENCE_JSON, "r") as file:
            persistence_data = json.load(file)

    # Update persistence.json with new hardware info
    persistence_data['GPU_INFO'] = gpu_info[:3]  # Store up to 3 GPUs
    persistence_data['CPU_INFO'] = cpu_info

    # Find and add installed llama.cpp binaries
    binaries = find_installed_binaries()
    persistence_data['AVAILABLE_BINARIES'] = binaries

    # Save back to persistence.json
    with open(PERSISTENCE_JSON, "w") as file:
        json.dump(persistence_data, file, indent=4)

def find_installed_binaries():
    """Detect installed llama.cpp binaries."""
    binary_folder = "./data/llama-binaries"
    installed_binaries = []
    if os.path.exists(binary_folder):
        installed_binaries = [f for f in os.listdir(binary_folder) if f.endswith(".zip")]
    return installed_binaries

def install_binaries(binary_type: str):
    """Install llama.cpp binaries for CPU or GPU."""
    with open(os.path.join(DATA_FOLDER, 'compatible_binaries.txt'), 'r') as f:
        compatible_binaries = f.read().splitlines()

    for binary in compatible_binaries:
        if binary_type == 'cpu' and not any(x in binary.lower() for x in ['cuda', 'vulkan', 'clblast', 'sycl', 'kompute']):
            download_and_extract(f"{GITHUB_BASE_URL}b3672/{binary}", LLAMA_BIN_DIR)
        elif binary_type == 'gpu' and any(x in binary.lower() for x in ['cuda', 'vulkan', 'clblast', 'sycl', 'kompute']):
            download_and_extract(f"{GITHUB_BASE_URL}b3672/{binary}", LLAMA_BIN_DIR)

def download_and_extract(url: str, target_dir: str):
    """Download and extract binaries from the given URL."""
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

def main():
    """Main function to handle hardware detection and save to persistence.json."""
    # Create necessary directories
    os.makedirs(DATA_FOLDER, exist_ok=True)
    os.makedirs(LLAMA_BIN_DIR, exist_ok=True)

    # Detect hardware
    gpu_info = get_gpu_info()
    cpu_info = get_cpu_info()

    # Save detected hardware info to persistence.json
    save_to_persistence_json(gpu_info, cpu_info)

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
            with open(PERSISTENCE_JSON, 'r') as f:
                hardware_info = json.load(f)
                print(json.dumps(hardware_info, indent=4))
        elif choice == '6':
            print("Exiting setup...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
