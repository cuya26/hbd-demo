import json
from typing import Optional

from fastapi import APIRouter
from fastapi import HTTPException
from pydantic import BaseModel

app = APIRouter()


class ModelParameters(BaseModel):
    temperature: Optional[float] = None
    top_k: Optional[int] = None
    top_p: Optional[float] = None
    repetition_penalty: Optional[float] = None
    max_tokens: Optional[int] = None
    mirostat_tau: Optional[float] = None


class Properties(BaseModel):
    userMessage: str
    systemMessage: str
    completionInit: str
    modelParameters: ModelParameters


class PromptingLog(BaseModel):
    prompt: str
    answer: str
    expected: str


@app.get('/get_properties/{task}')
async def get_properties(task: str):
    print(task)
    try:
        res = open('./MedInfoExt/resources/' + task + '.properties.json', 'r').read()
        res = json.loads(res)
        model_parameters = res['modelParameters']
        model_parameters = {k: v for k, v in model_parameters.items() if v is not None}
        res['modelParameters'] = model_parameters
        res = json.dumps(res)
    except FileNotFoundError:
        raise HTTPException(status_code=504, detail="File not found")

    return res



@app.post('/set_properties/{task}')
async def set_properties(task: str, properties: Properties):
    try:
        open('./MedInfoExt/resources/' + task + '.properties.json', 'w').write(properties.json())
    except FileNotFoundError:
        raise HTTPException(status_code=504, detail="File not found")
    return 'ok'


@app.get('/get_template')
async def get_template():
    try:
        res = open('./MedInfoExt/resources/template', 'r').read()
    except FileNotFoundError:
        raise HTTPException(status_code=504, detail="File not found")
    return res


@app.post('/log/{task}')
async def log(task: str, log: PromptingLog):
    import os
    from pathlib import Path
    from datetime import datetime
    now = datetime.now()
    print(now.strftime(task + "__%Y_%m_%d_%H_%M_%S.log"))
    logs = sorted(Path('./MedInfoExt/logs/').iterdir(), key=os.path.getmtime)
    last_log = [log for log in logs if log.name.startswith(task)]
    if len(last_log) > 0:
        last_log = open(last_log[-1], 'r').read()
    else:
        last_log = '{}'

    last_prompt_log = json.loads(last_log)
    current_prompt_log = json.loads(log.model_dump_json())
    if last_prompt_log == current_prompt_log:
        print('same log')
        return 'ok'
    else:
        print('new log')
        with open('./MedInfoExt/logs/' + now.strftime(task + "__%Y_%m_%d_%H_%M_%S.log"), 'w') as f:
            f.write(log.model_dump_json() + '\n')

    return 'ok'
