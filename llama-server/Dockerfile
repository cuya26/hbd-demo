FROM nvidia/cuda:12.1.1-devel-ubuntu22.04

RUN mkdir -p /workspace/
WORKDIR /workspace/
ENV TZ=Europe/Rome
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt-get update && apt-get upgrade -y \
    && apt-get install -y git build-essential \
    python3 python3-pip gcc wget cmake
# RUN git clone https://github.com/abetlen/llama-cpp-python/
COPY ./llama-cpp-python /workspace/
RUN python3 -m pip install --upgrade pip pytest cmake scikit-build setuptools fastapi uvicorn sse-starlette pydantic-settings starlette-context
# RUN CMAKE_ARGS="-DLLAMA_CUBLAS=on" FORCE_CMAKE=1 pip install ./
RUN CMAKE_ARGS="-DLLAMA_CUBLAS=on" FORCE_CMAKE=1 pip install llama-cpp-python[server]


# FROM python:3.10

# RUN mkdir -p /workspace/
# WORKDIR /workspace/
# ENV TZ=Europe/Rome
# RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
# RUN pip install llama-cpp-python[server]
# RUN apt-get update
# RUN yes | apt-get install libopenblas-dev cmake
# RUN CMAKE_ARGS="-DLLAMA_BLAS=ON -DLLAMA_BLAS_VENDOR=OpenBLAS" FORCE_CMAKE=1 pip install llama-cpp-python[server]