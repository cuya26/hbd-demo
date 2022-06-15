FROM pytorch/pytorch:1.10.0-cuda11.3-cudnn8-runtime

USER root
WORKDIR /workspace/
COPY requirements.txt ./
RUN pip install -r requirements.txt
