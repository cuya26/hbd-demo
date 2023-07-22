# FROM nvidia/cuda:11.4.3-devel-ubuntu20.04

# RUN mkdir -p /workspace/
# WORKDIR /workspace/
# ENV TZ=Europe/Rome
# RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
# RUN apt-get update
# RUN apt install -y python3 python3-pip cmake
# RUN CMAKE_ARGS="-DLLAMA_CUBLAS=on" FORCE_CMAKE=1 pip install llama-cpp-python[server]


FROM python:3.10

RUN mkdir -p /workspace/
WORKDIR /workspace/
ENV TZ=Europe/Rome
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN pip install llama-cpp-python[server]
# RUN apt-get update
# RUN yes | apt-get install libopenblas-dev cmake
# RUN CMAKE_ARGS="-DLLAMA_BLAS=ON -DLLAMA_BLAS_VENDOR=OpenBLAS" FORCE_CMAKE=1 pip install llama-cpp-python[server]