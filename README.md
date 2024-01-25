# HBD-Data-Project
## Working Group 1: Text Analysis
### HBD-Demo

This demo contains NLP models and system studied by the members of the working group 1 of the Health Big Data project

## Instruction for Test Installation

### Requirements
- 16GB RAM
- 40GB Solid Disk

### Installation with Ubuntu
- Install the last version of Docker([How to install](https://docs.docker.com/engine/install/ubuntu/))
- Install the last version of Docker-Compose([How to install](https://docs.docker.com/compose/install/linux/))
- Open terminal and clone the repo using the command ```git clone https://github.com/cuya26/hbd-demo```
- Move into the cloned folder using the command ```cd hbd-demo/```
- Modify in file axios.js the variable server_ip with the ip address of the machine that runs the demo
- Run the command ```docker-compose -f docker-compose-deploy.yml up -d``` to start the demo

#### Load document into patient search engine
- Copy your documents into ```patient-elastic-search/data/documents``` folder
- Install Python
- Move into the patient-elastic-search folder
- Install the python requirements with the command ```pip install -r requirements.txt```
- Move into the folder ```scripts```
- Run the script to load your documents ```python giuseppe_load_documents.py```



### Usage
- Open a browser with ```ip_of_the_demo_machine:51118```

## Instruction for Development

### Installation

- Run ```docker-compose up -d```
- Load the documents in the elastic-search engine:
    - Put the documents in the ```patient-elastic-search/data/documents```
    - Install the python requirements in ```patient-elastic-search/requirements.txt```
    - Run the script ```patient-elastic-search/script/giuseppe_load_documents.py```
- Look at the logs with ```docker-compose logs -f --tail=200```

### Project Structure

#### Frontend

##### Folder Structure
```md
frontend
├── Dockerfile
├── Dockerfile-Deploy
├── quasar.config.js
└── src
    ├── boot
    │   └── axios.js
    ├── components
    │   ├── ChatBot.vue
    │   ├── DeidentificationClassic.vue
    │   ├── MedicalInformationExtraction.vue
    │   ├── PatientSearch.vue
    │   ├── PharmacologicalEventExtraction.vue
    │   └── QuestionAnswering.vue
    ├── layouts
    │   └── MainLayout.vue
    └── pages
        └── IndexPage.vue
```
##### Description of the files
- **DockerFile**: is used to buid the image for development in ```hbd-demo/docker-compose.yml```
- **DockerFile-Deploy**: is used to buid the image for local testing. Need to be push into a docker-hub before to use it with ```hbd-demo/docker-compose-deploy.yml```
- **quasar.config.js**: is the config file of the quasar project. It can be used to change the port of the dev server
- **axios.js**: In this file the base urls of the backend api are defined
- **folder-components**: Each of this Vue.js component contains the html code and js script of the output card. Each component refer to a model task
- **MainLayout**: Contains the code of the header of the page (Page Title, Logos..)
- **IndexPage.vue** Contains the html and script code of the demo webpage. It contains mainly the parts of the file drop and text extraction interface. This vue page calls the task components

#### Backend

##### Folder Structure

```md
backend
├── api.py
├── config.json
├── data
│   └── checkpoints
│       ├── Bio_ClinicalBERT_model_trained_Action
│       ├── Bio_ClinicalBERT_model_trained_Actor
│       ├── Bio_ClinicalBERT_model_trained_Certainty
│       ├── Bio_ClinicalBERT_model_trained_disposition-type
│       ├── Bio_ClinicalBERT_model_trained_Negation
│       ├── Bio_ClinicalBERT_model_trained_Temporality
│       ├── medBIT-r3-plus_75
│       └── simplet5-epoch-6-train-loss-0.2724-val-loss-0.1477
|
├── Dockerfile
├── Dockerfile-Deploy
├── download_pretrained_models.py
├── ita_deidentification.py
├── model.py
└── requirements.txt
```

##### Description of the files
- **api.py**: is the file that runs the fastapi server and define all the api
- **confi.json**: is a config file for ita_deidentification. It is used to initialize the anonymizer class inside ita_deidentification
- **DockerFile**: is used to buid the image for development in ```hbd-demo/docker-compose.yml```
- **DockerFile-Deploy**: is used to buid the image for local testing. Need to be push into a docker-hub before to use it with ```hbd-demo/docker-compose-deploy.yml```
- **download_pretrained_models.py**: this script is use to download the models from huggingface during the building of the docker image (DockerFile and DockerFile-Deploy)
- **ita_deidentification.py**: this is the deidentification script that use regex, spacy(NER) and stanza(NER) to de-identify documents. The api.py import the function from this file for document de-identification
- **model.py**: this python file contains classes and functions for Question Answering, Drug Event Extraction, and the function for saliency map generation. The api.py import classes and function from it for information extraction tasks
- **download_pretrained_models.py**: this script is use to download the models from huggingface during the building of the docker image (DockerFile and DockerFile-Deploy)
- **requirements.txt**: contains all the requirements for the docker backend. It used to build docker image (DockerFile, DockerFile-Deploy)
- **data/checkpoints**: this folder contains the models used for pharmacological event extraction task (Bio_Clinical_Bert*, simplet5) used in model.py and a italian-medical version of bert (medBIT-r3-plus_75) that is used for question answering in the model.py file

#### llama-server

##### Folder Structure
```md
llama-server
├── Dockerfile
├── Dockerfile-Deploy
```

##### Description of the files
- **DockerFile**: is used to buid the image for development in ```hbd-demo/docker-compose.yml```
- **DockerFile-Deploy**: is used to buid the image for local testing. Need to be push into a docker-hub before to use it with ```hbd-demo/docker-compose-deploy.yml```

#### patient-elastic-search

##### Folder Structure
```md
patient-elastic-search
├── data
│   └── documents
├── notebooks
│   └── giuseppe_init_search_engine.ipynb
├── requirements.txt
└── scripts
    ├── giuseppe_load_documents.py
    └── giuseppe_translate_docs.py
```
##### Description of the files
- **data/documents**: Folder that contains the documents for information-retrieval
- **notebooks/giuseppe_init_search_engine.ipynb**: notebook that contains code to load documents into the elastic search system and inference
- **requirements.txt**: Python dependency needed to run the notebooks and the scripts in the folder
- **scripts/giuseppe_load_documents.py**: this script load the documents in ```data/documents``` into the elastic-search server
- **scripts/giuseppe_translate_docs.py**: this script translate the documents in the ```data/raw``` into italian

#### patient-elastic-search

##### Folder Structure
```md
patient-search-python-server
├── api.py
├── Dockerfile
└── requirements.txt
```
##### Description of the files
- **requirements.txt**: contains all the python requirements for the docker image. It used to build docker image (DockerFile, DockerFile-Deploy)
- **DockerFile**: is used to buid the image for development in ```hbd-demo/docker-compose.yml```
- **api.py**: fastapi server file that use the elastic search server
