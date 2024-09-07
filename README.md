# Llama-Legacy-Server
Status: Alpha. Very Early Stage, internet may cut out at some point, please support my work.

### Description:
It will host llama.cpp binaries suited to users hardware, utilizing the specificatlly relating llama.cpp pre-compiled binaries, utilizing compatibility with any cpp binary including non-continued ones, through only the `hello world` curl/json (lm studio compatible, possibly ollama too later).

## Development:
1. Assess End of Session 2 scripts, ensure completeness and correctness, of implementation, fix any issues and add required code, producing research as required.
2. Setup-Install Needs to Detect the amount of ram from both graphics cards using directx diagnostics, and also, `display ram capacity in menu` and `pass on in `.\data\persistance.json , that is read by main script when its run, that will be relevantly, calculating and distributing, the layers automatically on the cards, falling back to cpu when safe memory/threads usage on each of the cards exceeds user specified percent, ie the user is specifying, which cpus to use and which gpus, to use, so as for when the user then selects for example 65% then it will, 1) determine the number of layers on the model, 2) read the size of the model, and do the calculation`(model size + 10%) / number layers = MB per layer`, 3) read the memory size for the selected GPU from the json `(65% of memory size / MB per layer = number of layers to offload to GPU`, the remainder of the layers would be done on the CPU. We need to find the best/latest python v12 libraries for cpu/gpu identification and statistics. otherwise it would involve filtering directx output, which will require more work/fixing.

### Notes:
- code relating to the `hello world` curl...
```
curl http://localhost:1234/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{ 
    "model": "model-identifier",
    "messages": [ 
      { "role": "system", "content": "Always answer in rhymes." },
      { "role": "user", "content": "Introduce yourself." }
    ], 
    "temperature": 0.7, 
    "max_tokens": -1,
    "stream": true
}'
``` 
- List of binaries at relevant location `https://github.com/ggerganov/llama.cpp/releases/tag/b3680`
```
cudart-llama-bin-win-cu11.7.1-x64.zip - 293MB
cudart-llama-bin-win-cu12.2.0-x64.zip - 413MB
llama-b3672-bin-win-avx-x64.zip - 7.76MB
llama-b3672-bin-win-avx2-x64.zip - 7.76MB
llama-b3672-bin-win-avx512-x64.zip - 7.76MB
llama-b3672-bin-win-cuda-cu11.7.1-x64.zip - 145MB
llama-b3672-bin-win-cuda-cu12.2.0-x64.zip - 144MB
llama-b3672-bin-win-kompute-x64.zip - 8.04MB
llama-b3672-bin-win-llvm-arm64.zip - 11.4MB
llama-b3672-bin-win-msvc-arm64.zip - 13.4MB
llama-b3672-bin-win-noavx-x64.zip - 7.74MB
llama-b3672-bin-win-openblas-x64.zip - 18.8MB
llama-b3672-bin-win-sycl-x64.zip - 69.3MB
llama-b3672-bin-win-vulkan-x64.zip - 8.37MB
```
- Location of last known OpenCL binary `https://github.com/ggerganov/llama.cpp/releases/download/b3085/llama-b3085-bin-win-clblast-x64.zip`, for use with models produced before `June 2024`.

