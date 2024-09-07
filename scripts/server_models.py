# File: .\scripts\server_models.py

import os
import json
import time
import subprocess
from typing import Dict, Any, Generator
from flask import request, jsonify, Response, stream_with_context
from scripts.hardware_binaries import determine_best_binary, get_gpu_memory, get_system_memory, calculate_layers_for_gpu

def chat_completions(app, config: Dict[str, Any]):
    @app.route('/v1/chat/completions', methods=['POST'])
    def handle_chat_completions():
        data = request.json
        model_path = config.get('model', '')

        messages = data.get('messages', [])
        prompt = " ".join([f"{msg['role']}: {msg['content']}" for msg in messages])

        temperature = data.get('temperature', 0.7)
        max_tokens = data.get('max_tokens', -1)
        stream = data.get('stream', False)

        binary = determine_best_binary(config)
        gpu_memory = get_gpu_memory()
        system_memory = get_system_memory()

        command = [
            binary,
            '-m', model_path,
            '--prompt', prompt,
            '--temp', str(temperature),
            '-n', str(max_tokens) if max_tokens > 0 else '-1',
            '--interactive-first'
        ]

        if gpu_memory:
            layers = calculate_layers_for_gpu(gpu_memory, os.path.getsize(model_path), 32, 90)  # Assuming 32 layers and 90% GPU usage
            command.extend(['--n-gpu-layers', str(layers)])
        elif system_memory > 16:  # If system has more than 16GB RAM
            command.extend(['--mlock', '1'])

        if stream:
            return Response(stream_with_context(generate_stream(command, model_path)), content_type='text/event-stream')
        else:
            return generate_response(command, model_path)

    return handle_chat_completions

def generate_stream(command: list, model_path: str) -> Generator[str, None, None]:
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
        yield f"data: {json.dumps(chunk)}\n\n"

    yield f"data: {json.dumps({'choices': [{'delta': {}, 'finish_reason': 'stop'}]})}\n\n"

def generate_response(command: list, model_path: str) -> Response:
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