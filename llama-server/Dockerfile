FROM python:3.10

RUN mkdir -p /workspace/
WORKDIR /workspace/
ENV TZ=Europe/Rome
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN pip install llama-cpp-python[server]