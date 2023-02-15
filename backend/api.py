from fastapi import FastAPI, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from model import Predictor, question_and_answering_pipeline, compute_saliency_map_qa, compute_saliency_map_dee
from ita_deidentification import anonymizer
import pdfplumber
import pdftotext
from pdfminer.high_level import extract_text

app = FastAPI()
pred = Predictor()
deid = anonymizer('./config.json')

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

@app.post('/extract_data_table')
async def extract_data_table(request: Request):
    request_data = await request.json()
    input_text = request_data['input_text']
    data_list = pred.inference(input_text)
    return data_list

@app.post('/answer_question')
async def answer_question(request: Request):
    request_data = await request.json()
    input_text = request_data['input_text']
    question = request_data['question']
    model_type = request_data['model_type']
    model_name = request_data['model_name']
    model_lang = request_data['model_lang']
    compute_saliency_map = request_data['compute_saliency_map']
    answer_list = question_and_answering_pipeline(
        model_type, model_name,
        input_text,
        [question],
        model_lang,
        compute_saliency_map
    )
    return answer_list[0]

@app.post('/answer_question_list')
async def answer_question_list(request: Request):
    request_data = await request.json()
    input_text = request_data['input_text']
    model_type = request_data['model_type']
    model_name = request_data['model_name']
    model_lang = request_data['model_lang']
    compute_saliency_map = request_data['compute_saliency_map']
    question_answer_list = request_data['question_answer_list']
    question_list = [element['question'] for element in question_answer_list]
    return question_and_answering_pipeline(
            model_type,
            model_name,
            input_text,
            question_list,
            model_lang,
            compute_saliency_map
    )

@app.post('/deidentify')
async def deidentificate (request: Request):
    request_data = await request.json()
    input_text = request_data['input_text']
    # print('input_text:', input_text)
    cfg_dict = request_data['cfg']
    deid.load_dict(cfg_dict)
    deidentified_text = deid.deIdentificationIta(input_text)
    # print('deidentified_text:', deidentified_text)
    return { 'deidentified_text' : deidentified_text['text'] }

@app.post('/compute_saliency_map')
async def call_saliency_map_computation(request: Request):
    request_data = await request.json()
    task_type = request_data['task_type']
    if task_type == 'qa':
        input_text = request_data['input_text']
        answer_text = request_data['answer']
        slice_index = request_data['slice_index']
        question_text = request_data['question']
        model_type = request_data['model_type']
        model_name = request_data['model_name']
        model_lang = request_data['model_lang']
        saliency_map = compute_saliency_map_qa(
            input_text,
            answer_text,
            question_text,
            slice_index,
            model_type,
            model_name,
            model_lang
        )
        return { 'saliency_map' : saliency_map }
    if task_type == 'drug_event_extraction':
        input_text = request_data['input_text']
        sentence_text = request_data['sentence']
        target_text = request_data['target_text']
        task = request_data['task']
        model_type = request_data['model_type']
        model_name = request_data['model_name']
        model_lang = request_data['model_lang']
        saliency_map = compute_saliency_map_dee(
            input_text,
            sentence_text,
            target_text,
            model_type,
            model_name,
            model_lang,
            task
        )
        return { 'saliency_map' : saliency_map }

@app.post('/convert_pdf')
async def convert_pdf (uploaded_pdf: UploadFile):
    print("file:", uploaded_pdf.filename)
    print(uploaded_pdf)
    print(type(uploaded_pdf))
    # with pdfplumber.open(uploaded_pdf.file) as pdf:
    #     pdf_text = ''
    #     for page in pdf.pages:
    #         pdf_text += page.extract_text() + '\n'

    pdf = pdftotext.PDF(uploaded_pdf.file)
    pdf_text = "\n\n".join(pdf)

    return {'pdf_text': pdf_text }