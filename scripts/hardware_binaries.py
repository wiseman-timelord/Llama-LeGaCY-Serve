# File: .\scripts\hardware_binaries.py

import os
import nvidia_smi
import psutil
from typing import Dict, Any

LLAMA_BIN_DIR = "./data/llama-binaries"

def determine_best_binary(config: Dict[str, Any]) -> str:
    gpu_info = config.get("GPU_INFO", [])
    cpu_info = config.get("CPU_INFO", {})
    available_binaries = config.get("AVAILABLE_BINARIES", [])

    if gpu_info and "NVIDIA" in gpu_info[0]["graphics_brand"]:
        return os.path.join(LLAMA_BIN_DIR, next((b for b in available_binaries if "cuda" in b.lower()), None))
    elif gpu_info and "AMD" in gpu_info[0]["graphics_brand"]:
        return os.path.join(LLAMA_BIN_DIR, next((b for b in available_binaries if "vulkan" in b.lower()), None))
    else:
        return os.path.join(LLAMA_BIN_DIR, next((b for b in available_binaries if "avx2" in b.lower()), None))

def get_gpu_memory() -> float:
    try:
        nvidia_smi.nvmlInit()
        handle = nvidia_smi.nvmlDeviceGetHandleByIndex(0)
        info = nvidia_smi.nvmlDeviceGetMemoryInfo(handle)
        return info.total / 1024**3  # Convert to GB
    except:
        return None

def get_system_memory() -> float:
    return psutil.virtual_memory().total / 1024**3  # Convert to GB

def calculate_layers_for_gpu(vram: float, model_size: int, num_layers: int, gpu_percent: float) -> int:
    available_memory = vram * (gpu_percent / 100.0)
    memory_per_layer = (model_size * 1.10) / num_layers  # Add 10% buffer
    layers_for_gpu = available_memory // memory_per_layer
    return int(layers_for_gpu)

def list_available_binaries() -> list:
    return [f for f in os.listdir(LLAMA_BIN_DIR) if f.endswith('.exe')]
