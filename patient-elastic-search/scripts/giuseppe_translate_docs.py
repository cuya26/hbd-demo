from googletrans import Translator
import os
from tqdm import tqdm

translator = Translator()

docs_dir = '../data/raw/n2c2_2022/'
trans_docs_dir = '../data/processed/n2c2_2022_it/'
if not os.path.isdir(trans_docs_dir):
    os.mkdir(trans_docs_dir)
docs_filenames = [filename for filename in os.listdir(docs_dir) if '.txt' in filename]

for doc_filename in tqdm(docs_filenames):
    with open(f'{docs_dir}{doc_filename}') as f:
        doc_text = ''.join(f.readlines())
    doc_text = translator.translate(doc_text, src='en', dest='it').text
    with open(f'{trans_docs_dir}{doc_filename}', 'w') as f:
        f.write(doc_text)