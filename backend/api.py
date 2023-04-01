from fastapi import FastAPI, Request, UploadFile, Response
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from model import Predictor, question_and_answering_pipeline, compute_saliency_map_qa, compute_saliency_map_dee
from ita_deidentification import anonymizer
import pdfplumber
import pdftotext
from pdfminer.high_level import extract_text
import fitz
from io import BytesIO

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

def IntersecOfSets(array):
    s1 = set(array.pop(0))
    s2 = set(array.pop(0))
    result = s1.intersection(s2)
    if len(array) > 2:
      for element in array:
        result = result.intersection(element)

    # Converts resulting set to list
    final_list = list(result)
    return final_list

@app.post('/convert_pdf')
async def convert_pdf(uploaded_pdf: UploadFile):
    print("FILE: ", uploaded_pdf.filename)
    with fitz.open(stream=BytesIO(uploaded_pdf.file.read())) as document:
        if len(document) > 2:
            # ----- FIND DUPLICATES ----- #
            all_elements = []
            for page in document:
                elements = []
                for area in page.get_text('blocks'):
                    box = fitz.Rect(area[:4])
                    if not box.is_empty:
                        elements.append(area[4])
                all_elements.append(elements)
        duplicates = IntersecOfSets(all_elements) if len(document) > 2 else [] # all the elements that are in common within all pages

        # ----- REMOVE DUPLICATES AND CLEAN TEXT ----- #
        dirty_text = []                                             # collect the "dirty" to compare the line with the previous one
        clean_text = ''                                             # put the clean text
        header_text = ''                                            # put the header text
        header_missing = True                                       # when False because we are at page 2 and collected everything
        for page in document:
            all_linetext = []                                       # use to remove duplicate lines
            for element in page.get_text('blocks'):
                header = False                                      # True when text is part of the header 
                box = fitz.Rect(element[:4])
                if not box.is_empty:
                    if element[4] in duplicates:                     # check if normal text or header text
                        header = True
                    linetext = page.get_textpage(box).extractWORDS() # get all the single words (inside the box) and their positioning 
                    if linetext not in all_linetext:
                        all_linetext.append(linetext)
                        if linetext != []:
                            dirty_text.append(linetext[0])
                            if header_missing and header: 
                                header_text += linetext[0][4] + ' '
                            elif not header:
                                clean_text += linetext[0][4] + ' '
                        for line in linetext[1:]: 
                            x1 = abs(dirty_text[-1][0] - line[0])
                            x2 = abs(dirty_text[-1][1] - line[1])
                            x3 = abs(dirty_text[-1][2] - line[2])
                            x4 = abs(dirty_text[-1][3] - line[3])
                            if (x1+x2+x3+x4 > 4):                      # compare the position of each word to remove duplicates
                                #check if we are on the same line, in terms of coordinates or text recognition 
                                if(dirty_text[-1][1] == line[1] and dirty_text[-1][3] == line[3]) or (dirty_text[-1][6] == line[6]):
                                    if header_missing and header: 
                                        header_text += line[4] + ' '
                                    elif not header: 
                                        clean_text += line[4] + ' '
                                else:
                                    if header_missing and header: 
                                        header_text += '\n\n' + line[4] + ' '
                                    elif not header:
                                        clean_text += '\n\n' + line[4] + ' '

                                dirty_text.append(line)
                       
                        if header_missing and header: 
                            header_text += '\n\n\n' 
                        elif not header:
                            clean_text += '\n\n\n'
            header_missing = False   

        # ----- ADD DUPLICATES AT THE END AND RETURN TEXT ----- #
        clean_text += '\n\n ---------- HEADERS --------- \n'
        clean_text += header_text

        print('original type:', type(uploaded_pdf.file.read()))
              
        
        headers = {'Content-Disposition': 'attachment; filename="pymupdf.pdf"'}

        return {'pdf_text': clean_text, 
                'original_file': uploaded_pdf,
                }
    
@app.post('/return_pdf')
async def return_pdf(uploaded_pdf: UploadFile):
    out_pdf = './pymupdf.pdf'
    document =  fitz.open(stream=BytesIO(uploaded_pdf.file.read()), filetype='pdf')
    for page in document:
        for area in page.get_text('blocks'):
            box = fitz.Rect(area[:4])
            if not box.is_empty:
                page.add_rect_annot(box)
    
    output_pdf = BytesIO()
    document.save(out_pdf)
    output_pdf.seek(0)
    return FileResponse(out_pdf, filename='pymupdf.pdf')
        


