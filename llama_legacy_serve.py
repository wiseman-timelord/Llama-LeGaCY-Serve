# Script: .\llama_legacy_serve.py

# Imports
import os
import subprocess
import json
from flask import Flask, request, jsonify, Response, stream_with_context
import time

# Globals
app = Flask(__name__)

# Path to persistence file (now JSON)
persistence_file = "./data/persistence.json"

# Function to load JSON configuration
def load_json_config():
    if os.path.exists(persistence_file):
        with open(persistence_file, "r") as f:
            return json.load(f)
    return {}

# Function to save JSON configuration
def save_json_config(config):
    with open(persistence_file, "w") as f:
        json.dump(config, f, indent=4)

# Function to list all models in the specified directory
def list_models(model_dir):
    models = []
    for root, dirs, files in os.walk(model_dir):
        for file in files:
            if file.lower().endswith((".ggml", ".bin", ".gguf")):
                models.append(file)
    return models

# Function to display the menu
def display_menu(config):
    gpu_info = config.get("GPU_INFO", [])
    cpu_info = config.get("CPU_INFO", {})
    model_dir = config.get("MODEL_DIR", "./models")
    models = list_models(model_dir)

    print(f"\n===== LMS-Local Menu =====")
    
    # Display GPU Info
    print("GPU Configuration:")
    for idx, gpu in enumerate(gpu_info, start=1):
        print(f"GPU {idx}: {gpu['graphics_brand']} - {gpu['graphics_name']}, Shaders: {gpu['graphics_total_shaders']}, VRAM: {gpu['graphics_total_vram']} MB")

    # Display CPU Info
    print(f"\nCPU Configuration: {cpu_info.get('processor_brand', 'Unknown')} - {cpu_info.get('processor_name', 'Unknown')}, Threads: {cpu_info.get('processor_total_threads', 'Unknown')}, RAM: {cpu_info.get('processor_total_ram', 0):.2f} MB")

    print(f"\nAvailable models in {model_dir}:")
    for idx, model in enumerate(models, start=1):
        print(f"{idx}. {model}")
    print("\n1. Select model")
    print("2. Specify GPU memory usage percent")
    print("3. Start server")
    print("4. Exit")
    print(f"==========================")

    return input("Choose an option: "), models

# Function to update the persistence file (JSON)
def update_persistence(key, value):
    config = load_json_config()
    config[key] = value
    save_json_config(config)

# Function to start the server
def start_server(config, models):
    model_dir = config.get("MODEL_DIR", "./models")
    model_idx = int(input(f"Select model (1-{len(models)}): ")) - 1
    if 0 <= model_idx < len(models):
        model_path = os.path.join(model_dir, models[model_idx])
        update_persistence('model', model_path)
        print(f"Server started with model: {model_path}")
        app.run(host='0.0.0.0', port=1234)
    else:
        print("Invalid model selection.")

# Helper function to format llama-cli output as SSE
def format_sse(data: str) -> str:
    return f"data: {json.dumps(data)}\n\n"

# API endpoint
@app.route('/v1/chat/completions', methods=['POST'])
def chat_completions():
    data = request.json
    config = load_json_config()
    model_path = config.get('model', '')

    messages = data.get('messages', [])
    prompt = " ".join([f"{msg['role']}: {msg['content']}" for msg in messages])

    temperature = data.get('temperature', 0.7)
    max_tokens = data.get('max_tokens', -1)
    stream = data.get('stream', False)

    # Determine the best binary to use (to be defined based on model and hardware)
    binary = determine_best_binary(config)

    # Construct llama-cli command
    command = [
        binary,
        '-m', model_path,
        '--prompt', prompt,
        '--temp', str(temperature),
        '-n', str(max_tokens) if max_tokens > 0 else '-1',
        '--interactive-first'
    ]

    def generate():
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

        for line in process.stdout:
            chunk = {
                "id": f"chatcmpl-{int(time.time())}",
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": model_path,
                "choices": [
                    {
                        "delta": {"content": line.strip()},
                        "index": 0,
                        "finish_reason": None
                    }
                ]
            }
            yield format_sse(chunk)

        # Send the final chunk
        final_chunk = {
            "id": f"chatcmpl-{int(time.time())}",
            "object": "chat.completion.chunk",
            "created": int(time.time()),
            "model": model_path,
            "choices": [
                {
                    "delta": {},
                    "index": 0,
                    "finish_reason": "stop"
                }
            ]
        }
        yield format_sse(final_chunk)

    if stream:
        return Response(stream_with_context(generate()), content_type='text/event-stream')
    else:
        # For non-streaming, collect all output and send as a single response
        process = subprocess.run(command, capture_output=True, text=True)
        response = {
            "id": f"chatcmpl-{int(time.time())}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model_path,
            "choices": [
                {
                    "message": {"role": "assistant", "content": process.stdout.strip()},
                    "finish_reason": "stop",
                    "index": 0
                }
            ]
        }
        return jsonify(response)

# Function to calculate layers and distribute them across available hardware
def calculate_layers_for_gpu(vram, model_size, num_layers, gpu_percent):
    """Calculate the number of layers to offload to each GPU."""
    available_memory = vram * (gpu_percent / 100.0)
    memory_per_layer = (model_size * 1.10) / num_layers  # Add 10% buffer
    layers_for_gpu = available_memory // memory_per_layer
    return int(layers_for_gpu)

# Main function to display menu and run actions
def main():
    config = load_json_config()

    while True:
        choice, models = display_menu(config)

        if choice == "1":
            model_dir = input("Enter model directory: ")
            update_persistence("MODEL_DIR", model_dir)
        elif choice == "2":
            gpu_percent = float(input("Enter GPU memory percentage to use (e.g., 65): "))
            update_persistence("gpu_percent", gpu_percent)
        elif choice == "3":
            start_server(config, models)
        elif choice == "4":
            print("Exiting...")
            break
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()
