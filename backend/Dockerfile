FROM python:3.9

RUN mkdir -p /workspace/
WORKDIR /workspace/
COPY requirements.txt /workspace/
RUN apt-get update
ENV TZ=Europe/Rome
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN yes | apt-get install apt-utils build-essential libpoppler-cpp-dev pkg-config
RUN yes | apt-get install cmake git
RUN pip install --no-cache-dir --upgrade -r requirements.txt
RUN python3 -m spacy download it_core_news_lg
COPY ita_deidentification.py /workspace/
COPY config.json /workspace/
RUN python3 ita_deidentification.py
ENTRYPOINT ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "5003", "--reload"]
