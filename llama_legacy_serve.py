# Script: .\llama_legacy_serve.py
import os
import subprocess
import json
import yaml
from flask import Flask, request, jsonify, Response, stream_with_context
import time

app = Flask(__name__)

# Path to persistence file
persistence_file = "./data/persistence.yaml"

# Function to load YAML configuration
def load_yaml_config():
    if os.path.exists(persistence_file):
        with open(persistence_file, "r") as f:
            return yaml.safe_load(f)
    return {}

# Function to save YAML configuration
def save_yaml_config(config):
    with open(persistence_file, "w") as f:
        yaml.dump(config, f)

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
    gpu_type = config.get("GPU_TYPE", "CPU")
    threads = config.get("THREADS", "4")
    layers = config.get("LAYERS", "All")
    model_dir = config.get("MODEL_DIR", "./models")

    models = list_models(model_dir)

    print(f"\n===== LMS-Local Menu =====")
    print(f"1. GPU/CPU: {gpu_type}")
    print(f"2. Threads: {threads}")
    print(f"3. Layers on GPU: {layers}")
    print(f"4. Model Library: {model_dir}")
    print(f"\nAvailable models in {model_dir}:")
    for idx, model in enumerate(models, start=1):
        print(f"{idx}. {model}")
    print(f"\n5. Start server")
    print(f"6. Exit")
    print(f"==========================")

    choice = input("Select an option (1-6): ")
    return choice, models

# Function to update the persistence file
def update_persistence(key, value):
    config = load_yaml_config()
    config[key] = value
    save_yaml_config(config)

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
@app.route('/v1/chat/completions', methods=['POST'])
def chat_completions():
    data = request.json
    config = load_yaml_config()
    model_path = config.get('model', '')
    
    messages = data.get('messages', [])
    prompt = " ".join([f"{msg['role']}: {msg['content']}" for msg in messages])
    
    temperature = data.get('temperature', 0.7)
    max_tokens = data.get('max_tokens', -1)
    stream = data.get('stream', False)

    # Determine the best binary to use
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

# Main function to display menu and run actions
def main():
    config = load_yaml_config()
    
    while True:
        choice, models = display_menu(config)

        if choice == "1":
            print("Current GPU/CPU configuration:", ", ".join(config.get("GPU_TYPE", ["CPU"])))
            print("Available VRAM:")
            for gpu, vram in config.get("VRAM_CAPACITY", {}).items():
                print(f"  {gpu}: {vram:.2f} MB")
            # You might want to add options to modify GPU usage or priorities here
        elif choice == "2":
            new_threads = input("Enter number of threads: ")
            update_persistence("THREADS", new_threads)
        elif choice == "3":
            new_model_dir = input("Enter new model library path: ")
            update_persistence("MODEL_DIR", new_model_dir)
        elif choice == "4":
            start_server(config, models)
        elif choice == "5":
            print("Exiting...")
            break

if __name__ == "__main__":
    main()