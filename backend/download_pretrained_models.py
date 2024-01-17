from transformers import AutoModel, AutoTokenizer

models = [
    'valhalla/t5-base-qa-qg-hl',
    'Narrativa/mT5-base-finetuned-tydiQA-xqa',
    'deepset/xlm-roberta-large-squad2'
]

tokenizers = [
    't5-large',
    'bert-base-cased',
    'emilyalsentzer/Bio_ClinicalBERT'
]

for model_name in models:
    AutoModel.from_pretrained(model_name)
    AutoTokenizer.from_pretrained(model_name)

for tokenizer_name in tokenizers:
    AutoTokenizer.from_pretrained(tokenizer_name)
