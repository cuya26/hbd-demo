from bs4 import ResultSet
from simplet5 import SimpleT5
from os import path
import torch
from transformers import AutoTokenizer

class Predictor:
    def __init__(self) -> None:
        self.model = SimpleT5()
        checkpoint_name = 'simplet5-epoch-6-train-loss-0.2724-val-loss-0.1477'
        self.model.load_model("t5","data/checkpoints/"+checkpoint_name, use_gpu=False)
        self.tokenizer = AutoTokenizer.from_pretrained('t5-large')

    def inference(self, input_text):
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
        entity_list = [entity.lower().strip() for entity in entity_list if entity.strip() != '']
        

        results_with_pos =[]
        for entity in entity_list:   
            for punctuation in [',', '.', ' ', '\n', '\t', ':', ';', '(', '[', '{']:
                search_start = 0
                # if entity == 'ativan':
                #   print(f"entity : {entity} with pucntuation: {punctuation}  was found with start point {original_text.lower().find(punctuation + entity, search_start)}")
                while input_text.lower().find(punctuation + entity, search_start) != -1:
                    start = input_text.lower().find(punctuation + entity, search_start) + 1
                    end = start + len(entity)
                    search_start = end
                    pos = [start, end]
                    results_with_pos.append([entity, pos])
        print('results with pos', results_with_pos)
        filtered_entities, pos_entities = zip(*results_with_pos)
        # print(entity_list)
        return filtered_entities