# Llama-LeGaCY-Server
It will host llama.cpp binaries suited to users hardware, utilizing the specificatlly relating llama.cpp pre-compiled binaries, utilizing compatibility with the `hello world` curl/json.

- Work..
1. Assess End of Session 1 scripts, ensure completeness and correctness, of implementation, fix any issues and add required code, producing research as required.
2. Assess code relating to the `hello world` curl...
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
3. ensure that cpp menu is correctly implemented, this...
```
cudart-llama-bin-win-cu11.7.1-x64.zip - 293MB
cudart-llama-bin-win-cu12.2.0-x64.zip - 413MB
llama-b3672-bin-macos-arm64.zip - 50MB
llama-b3672-bin-macos-x64.zip - 51.8MB
llama-b3672-bin-ubuntu-x64.zip - 55.6MB
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
...is supposed to be a list in the code, that is selected dynamically based on the relating hardware present, obviously this batch will be intended for windows only, so things for mac and linux should be removed to streamline. With a relating global variable relating to `%LLAMA_BINARIES_ACTIVE%`, which would be a shortlist from the files listed based on users hardware, which whatever could be detected would be displayed beforehand, so as to know what relating binaries to ues. If lists is beyond batch, then we will need to move most of the code to `install_setup.py`.
4. Need to find last version that supported OpenCL, to add options for compare/compatibility for AMD. Last version to support it is `https://github.com/ggerganov/llama.cpp/releases/download/b3085/llama-b3085-bin-win-clblast-x64.zip`. user of for example non-ROCM AMD card such as `RX 470` would then have options clblast and vulkan, but presumably clblast would not work for llama 3.1 and such newer model formats.
- Setup-Install Needs to Detect the amount of ram from both graphics cards using directx diagnostics, and also, `display ram capacity in menu` and `pass on in `.\data\persistance.txt` to the main script, that will be relevantly, calculating and distributing, the layers automatically on the cards, falling back to cpu when safe memory/threads usage on each of the cards exceeds user specified percent, by default 65% spread equally between all resources, so the number of layers relevant to the model will be spread among the llama cpp resources available, that have been detected. We need to find python v12 libraries for cpu/gpu identification and statistics. otherwise it would involve filtering directx output, which will require more fixing.
