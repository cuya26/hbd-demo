import json

import requests
from fastapi import Request, APIRouter
from haystack.document_stores import ElasticsearchDocumentStore
from haystack.nodes import BM25Retriever
from haystack.nodes import FARMReader
from haystack.pipelines import ExtractiveQAPipeline

app = APIRouter()

# reader = FARMReader(model_name_or_path="/models/medBIT-r3-plus_75/", use_gpu=False)
reader = FARMReader(model_name_or_path="IVN-RIN/medBIT-r3-plus", use_gpu=False)

document_store = ElasticsearchDocumentStore(
    host='elasticsearch',  # 'host.docker.internal',
    port=9200,
    username="",
    password=""
)

retriever = BM25Retriever(document_store=document_store)

pipe = ExtractiveQAPipeline(reader, retriever)

# This will act as our "cache"
# cache: Dict[str, List[Dict]] = {}

outputs_list = []


@app.post('/patient_search')
async def patient_search(request: Request):
    request_data = await request.json()
    query = request_data['query']
    prediction = pipe.run(
        query=query,
        params={
            "Retriever": {"top_k": 10},
            "Reader": {"top_k": 10}
        }
    )

    outputs = []
    for document in prediction['documents']:
        output_dict = {}
        output_dict['text'] = document.content
        output_dict['document_score'] = document.score
        output_dict['document_id'] = document.id[0:5]
        for answer in prediction['answers']:
            # print(answer.document_ids[0])
            if (answer.document_ids[0] == document.id):
                output_dict['context'] = answer.context
                output_dict['answer'] = answer.answer
        outputs.append(output_dict)

    # Store the results in the cache
    outputs_list.append(outputs)
    # cache[query] = outputs
    return {'output': outputs}


@app.post('/criteria_check')
async def criteria_check(request: Request):
    request_data = await request.json()
    criteria = request_data['criteria']
    # query = request_data['query']
    # patient_search_output = cache.get(query, [])
    # patient_search_output = await patient_search(request)
    patient_search_output = outputs_list[-1] if outputs_list else []
    i_criteria = []
    for document in patient_search_output:
        prompt = f'''Given the following clinical text:
        ```
        {document['text']}
        ```
        and given the following eligibility inclusion criteria for a clinical trial:
        ```
        {criteria}
        ```
        Determine whether the patient would be elegible for the clinical trial, responding either "Elegible, because ...", "Potentially elegible, if ..." or "Not elegible, because ..."  
        Response: 
        '''
        # If it contains multiple inclusion criterias, re-write those criterias in the following format:
        # Criterion 1 - …
        # Criterion 2 - …
        # …
        # Criterion N - …
        # Then answer with the format like: YES, it is
        # '''
        answer = ask_to_llm(prompt)
        i_criteria.append(answer)
    # i_criteria = ["yes", "no", "yes"]
    in_criteria = []
    for document in i_criteria:
        output_dict = {}
        output_dict['text'] = document
        in_criteria.append(output_dict)

    return {'criteria': in_criteria}


def ask_to_llm(prompt, system_message="You are a helpful assistant and a medical expert"):
    data = {
        "messages": [
            {
                "content": system_message,
                "role": "system"
            },
            {
                "content": prompt,
                "role": "user"
            }
        ],
        'temperature': 0,
        'max_tokens': 500,
        # 'mirostat_tau': 0.0
    }
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = requests.post(
        "http://131.175.15.22:61111/llama-server/v1/chat/completions/",
        # "http://host.docker.internal:51124/v1/chat/completions",
        headers=headers,
        json=data
    )

    if response.ok:
        completion_json = json.loads(response.text)
        completion_text = completion_json['choices'][0]['message']['content']
        return completion_text
    else:
        raise ValueError(f"Request problem. Status Code: {response.status_code}")
