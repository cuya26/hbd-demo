FROM python:3.10

RUN mkdir -p /workspace/
WORKDIR /workspace/
COPY requirements.txt /workspace/
RUN pip install --upgrade -r requirements.txt
ENTRYPOINT ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "5003", "--reload"]