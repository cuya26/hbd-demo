FROM python:3.10

RUN mkdir -p /workspace/
WORKDIR /workspace/
ENV TZ=Europe/Rome
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt-get update
RUN yes | apt-get install libopenblas-dev cmake
RUN CMAKE_ARGS="-DLLAMA_OPENBLAS=on" FORCE_CMAKE=1  pip install llama-cpp-python[server]