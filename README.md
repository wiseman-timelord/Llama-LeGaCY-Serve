# llaMa-LeGaCY-SerVer
It will host llama.cpp binaries suited to users hardware, utilizing the specificatlly relating llama.cpp pre-compiled binaries, utilizing compatibility with the `hello world` curl/json.

- Currentl implemented binaries...
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

- Work..
1. Assess End of Session 1 scripts, ensure completeness and correctness, of implementation, fix any issues and add required code, producing research as required.
2. ensure that cpp menu is correctly implemented, this...
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
...is supposed to be a list in the code, that is selected dynamically based on the relating hardware present, obviously this batch will be intended for windows only, so things for mac and linux should be removed to streamline. With a relating global variable relating to `%LLAMA_BINARIES_ACTIVE%%, which would be a shortlist from the files listed based on users hardware, which whatever could be detected would be displayed beforehand, so as to know what relating binaries to ues. 
