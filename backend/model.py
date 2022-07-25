from googletrans import Translator
from pyparsing import null_debug_action
from simplet5 import SimpleT5
from os import path
import torch
from transformers import AutoTokenizer, QuestionAnsweringPipeline, pipeline, LongformerForSequenceClassification, BertForSequenceClassification, AutoModelForSequenceClassification
import spacy
from transformers import AutoTokenizer, AutoModelForQuestionAnswering, pipeline
import re
nlp = spacy.load("en_core_sci_md")

def question_and_answering_pipeline(model_type, model_name, input_text, question_list):
    # input preprocessing
    input_text = re.sub(" +", ' ', input_text)
    input_text = re.sub("\s*\n\s*(\s*\n\s*)+", '\n\n', input_text)
    input_text = re.sub("\t+|\t ", ' ', input_text)
    input_text = re.sub(" +", ' ', input_text)
    input_text = input_text.lower()

    if model_type == 'generative':
        task = "multitask-qa-qg"
    else:
        task = 'question-answering'

    nlp = pipeline(task, model=model_name, tokenizer=model_name)

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    input_text_ids = tokenizer.encode(
        input_text,
        return_tensors='pt',
        add_special_tokens=True
    )
    text_slices = []
    start_slice = 0
    max_lenght = 500
    # print('slicing...')
    for end_slice in range(max_lenght, input_text_ids.shape[1], max_lenght):
        text_slices.append(tokenizer.decode(input_text_ids[0, start_slice:end_slice], skip_special_tokens=True))
        start_slice = end_slice
    text_slices.append(tokenizer.decode(input_text_ids[0,start_slice:], skip_special_tokens=True))
    # print('end slicing')
    answer_list = []
    for question in question_list:
        print(f'answering question: {question}')
        answers = []
        for index, text_slice in enumerate(text_slices):
            qa_input = {
                'question': question,
                'context': text_slice,
            }
            answer_dict = nlp(qa_input)
            if answer_dict["score"] > 0.2:
                # answers.append(f'Answer text slice {index + 1}: {answer_dict["answer"]}, score: {"{:.2f}".format(answer_dict["score"]*100)}%')
                answers.append(f'Answer text slice {index + 1}: {answer_dict["answer"]}')
        if len(answers) == 1:
            answer = answers[0].split(': ')[1]
        elif len(answers)==0:
            answer = "L'informazione non è presente nel testo"
        else:
            answer = '\n'.join(answers)
        answer_list.append({ 'question': question, 'answer': answer})
    return answer_list

class Predictor:
    def __init__(self) -> None:
        # self.model = SimpleT5()
        # checkpoint_name = 'simplet5-epoch-6-train-loss-0.2724-val-loss-0.1477'
        # self.model.load_model("t5","data/checkpoints/"+checkpoint_name, use_gpu=True)
        # self.tokenizer = AutoTokenizer.from_pretrained('t5-large')
        self.translator = Translator()
        self.model = None
        self.tokenizer = None

        self.ctx_cats = {}
        self.ctx_cats['Action'] = {'Inzio':0, 'Fine':1, 'Incremento':2, 'Decremento':3, 'Altri cambiamenti':4, 'Unica dose':5, 'Sconociuto':6}
        self.ctx_cats['Negation'] = {'Si':0, 'No':1}
        self.ctx_cats['Temporality'] = {'Passato':0,'Presente':1,'Futuro':2,'Sconosciuto':3}
        self.ctx_cats['Certainty'] = {'Certo':0, 'Ipotetico':1, 'Condizionale':2, 'Sconosciuto':3}
        self.ctx_cats['Actor'] = {'Medico':0, 'Paziente':1, 'Sconosciuto':2}
        self.ctx_cats['disposition-type'] = {'Disposizione':0,'Nessuna Disposizione':1,'Indeterminato':2}

    def inference(self, input_text):
        self.model = SimpleT5()
        checkpoint_name = 'simplet5-epoch-6-train-loss-0.2724-val-loss-0.1477'
        self.model.load_model("t5","data/checkpoints/"+checkpoint_name, use_gpu=True)
        self.tokenizer = AutoTokenizer.from_pretrained('t5-large')

        input_text = self.translator.translate(input_text, src='it', dest='en').text
        text = input_text.replace('\t', ' ').replace('\n', ' ')
        text_filtered = ''
        for char_index, char in enumerate(text):
            if char_index < (len(text)-1):
                if not(text[char_index + 1] == ' ' and char == ' '):
                    text_filtered += char
        text_filtered = text_filtered.lower() # uncase the text
        # print(text_filtered)
        attribute = 'medications: '
        # input_text = bos + text_filtered + sep + attribute
        input_text_ids = self.tokenizer.encode(
            text_filtered,
            return_tensors='pt',
            add_special_tokens=True
        )
        print('fino a qui tutto bene init')
        # If a text is longer than 900 tokens I create slices to divide it
        text_slices = []
        start_slice = 0
        max_lenght = 250
        print('slicing...')
        for end_slice in range(max_lenght, input_text_ids.shape[1], max_lenght):
            text_slices.append(self.tokenizer.decode(input_text_ids[0, start_slice:end_slice], skip_special_tokens=True))
            start_slice = end_slice
        text_slices.append(self.tokenizer.decode(input_text_ids[0,start_slice:], skip_special_tokens=True))
        print('end slicing')
        
        # print(text_slices)
        # break
        # gpt2 small can only manage 1000 tokens, I divide the text in more parts and
        # give them as different input and the aggregate the results
        entity_list = []
        for text_slice in text_slices:
            print('results for the slice')
            # text_slice = self.translator.translate(text_slice, src='it', dest='en').text
            results = self.model.predict(
                attribute + text_slice,
                num_beams=2,
                top_k=0,
                top_p=1,
                do_sample=False,
                repetition_penalty=0.5,
                length_penalty=0.4,
                early_stopping=True,
            )[0]
            entity_list += results.split(',')

            # print('results:', results)
        print('entity_list:', entity_list)
        entity_list = list(set(entity_list))
        entity_list = [
            entity.lower().strip() for entity in entity_list\
            if entity.strip() != ''
        ]

        def slice_txt(text, value): #truncate centered on drug name for long sentences
            try:
                if len(text) > 512:
                    start = max(0, text.index(value.lower())-256)
                    return text[start:start+512]
                return text
            except ValueError:
                print(text, '\n', value)

        final_results = []
        doc = nlp(input_text)
        del self.model
        del self.tokenizer

        self.model = BertForSequenceClassification.from_pretrained('data/checkpoints/model_trained_disposition-type/')
        self.tokenizer = AutoTokenizer.from_pretrained('emilyalsentzer/Bio_ClinicalBERT')
        
        self.model.eval()
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        self.model.to(device)
        inv_map = {v: k for k, v in self.ctx_cats['disposition-type'].items()}
        generator = pipeline(task="text-classification", model=self.model, tokenizer=self.tokenizer, device=0) #device=0 per gpu, -1 per cpu
        def get_label(text):
            return inv_map[int(generator(text)[0]['label'][-1])]
        # translated_text = self.translator.translate(text_filtered, src='it', dest='en').text
        for entity in entity_list:
            for punctuation in [',', '.', ' ', '\n', '\t', ':', ';', '(', '[', '{']:
                search_start = 0
                # if entity == 'ativan':
                #   print(f"entity : {entity} with pucntuation: {punctuation}  was found with start point {original_text.lower().find(punctuation + entity, search_start)}")
                while input_text.lower().find(punctuation + entity, search_start) != -1:
                    start = input_text.lower().find(punctuation + entity, search_start) + 1
                    end = start + len(entity)
                    search_start = end
                    sentence = doc.char_span(start, end, alignment_mode='expand').sent.text
                    sentence = ''.join(sentence).replace('\n', ' ').replace('\t', ' ').replace('\u2006', ' ') # I replace the new lines and the tabs with spaces
                    text_filtered = ''
                    for char_index, char in enumerate(sentence):
                        if char_index < (len(sentence)-1):
                            if not(sentence[char_index + 1] == ' ' and char == ' '):
                                text_filtered += char
                    sentence = text_filtered.lower() # uncase the text
                    sentence = slice_txt(sentence, entity)
                    sentence = entity + ' : ' + sentence
                    # sentence = self.translator.translate(sentence, src='it', dest='en').text
                    disposition = get_label(sentence)
                    final_results.append(dict(disposition=disposition, sentence=sentence, entity=entity, pos=dict(start=start, end=end)))
                

        # print('try')
        # self.model = BertForSequenceClassification.from_pretrained('data/checkpoints/Bio_ClinicalBERT_model_trained_Action/')
        # print('it works')
        del self.model
        contexts = [
            'Action',
            'Actor',
            'Temporality',
            'Certainty',
            'Negation'
        ]
        for context in contexts:
            self.model = BertForSequenceClassification.from_pretrained(f'data/checkpoints/Bio_ClinicalBERT_model_trained_{context}/')
            self.model.eval()
            # self.model.to(device)
            inv_map = {v: k for k, v in self.ctx_cats[context].items()}
            generator = pipeline(task="text-classification", model=self.model, tokenizer=self.tokenizer, device=0) #device=0 per gpu, -1 per cpu
            def get_label(text):
                return inv_map[int(generator(text)[0]['label'][-1])]

            for result_index, single_result in enumerate(final_results):
                if single_result['disposition'] == 'Disposizione':
                    # print(single_result)
                    final_results[result_index][context] = get_label(single_result['sentence'])

        del self.model
        del self.tokenizer
        return final_results