from fastapi import FastAPI, Request, UploadFile, Response
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from haystack.document_stores import ElasticsearchDocumentStore
from haystack.nodes import BM25Retriever
from haystack.pipelines import ExtractiveQAPipeline
from haystack.nodes import FARMReader
import json

reader = FARMReader(model_name_or_path="/models/medBIT-r3-plus_75/", use_gpu=False)

# Get the host where Elasticsearch is running, default to localhost
# host = os.environ.get("ELASTICSEARCH_HOST", "localhost")

document_store = ElasticsearchDocumentStore(
    host='host.docker.internal',
    port=9202,
    username="",
    password=""
)

retriever = BM25Retriever(document_store=document_store)

pipe = ExtractiveQAPipeline(reader, retriever)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http:\/\/131\.175\.120\.138:61111\/hbd-demo\/*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        output_dict['document_id'] = document.id
        for answer in prediction['answers']:
            # print(answer.document_ids[0])
            if (answer.document_ids[0] == document.id):
                output_dict['context'] = answer.context
                output_dict['answer'] = answer.answer
        outputs.append(output_dict)

    return { 'output': outputs}