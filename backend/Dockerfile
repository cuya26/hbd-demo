FROM johnsnowlabs/sparknlp:sparknlp_for_healthcare_jupyter

RUN mkdir -p /workspace/
WORKDIR /workspace/
COPY spark_jsl.json /workspace/sparknlp_keys.json
COPY install_jsl.sh /workspace/
RUN chmod +x install_jsl.sh
RUN /workspace/install_jsl.sh
COPY requirements.txt /workspace/
RUN apt-get update
ENV TZ=Europe/Rome
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN yes | apt-get install apt-utils build-essential libpoppler-cpp-dev pkg-config
RUN pip install --no-cache-dir --upgrade -r requirements.txt
RUN python3 -m spacy download it_core_news_lg
ENTRYPOINT ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "5003", "--reload"]
