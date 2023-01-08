from googletrans import Translator
from simplet5 import SimpleT5
from os import path
import torch
import spacy
from transformers import AutoTokenizer, pipeline, AutoModelForSeq2SeqLM, AutoModelForSequenceClassification, BertForSequenceClassification
import re
import numpy as np
from torch.nn import functional as F
from captum.attr import InputXGradient
from functools import partial
from operator import attrgetter
from tqdm import tqdm
import time


DEVICE = torch.device('cpu')
MAX_LENGHT = 301

def _get_embeddings(input_ids, model, model_type) -> torch.FloatTensor:
    """
    Get token embeddings and one-hot vector into vocab. It's done via matrix multiplication
    so that gradient attribution is available when needed.
    Args:
        input_ids: Int tensor containing token ids. Of length (sequence length).
        Generally returned from the the tokenizer such as
        lm.tokenizer(text, return_tensors="pt")['input_ids'][0]
    Returns:
        inputs_embeds: Embeddings of the tokens. Dimensions are (sequence_len, d_embed)
        token_ids_tensor_one_hot: Dimensions are (sequence_len, vocab_size)
    """
    if 't5' in model_type:
        embedding_matrix = model.shared.weight
    if 'bert' in model_type:
        embedding_matrix = model.bert.embeddings.word_embeddings.weight

    vocab_size = embedding_matrix.shape[0]
    batch_size, num_tokens = input_ids.shape
    one_hot_tensor = torch.zeros(batch_size, num_tokens, vocab_size, device=DEVICE).scatter_(-1, input_ids.unsqueeze(-1), 1.)
    token_ids_tensor_one_hot = one_hot_tensor.clone().requires_grad_(True)

    inputs_embeds = torch.matmul(token_ids_tensor_one_hot, embedding_matrix)
    return inputs_embeds

def custom_forward_func_seq_cla(inputs_embeds, decoder_input_embeds, input_attention_mask, model):
    output = model(
        inputs_embeds=inputs_embeds,
        attention_mask=input_attention_mask,
        return_dict=True
    )
    return torch.softmax(output.logits, dim=-1)

def custom_forward_generative(input_embeds: torch.Tensor, decoder_input_embeds: torch.Tensor, input_attention_mask: torch.Tensor, model) -> torch.Tensor:
    if decoder_input_embeds is not None:
        output = model(
            inputs_embeds=input_embeds,
            attention_mask=input_attention_mask,
            decoder_inputs_embeds=decoder_input_embeds,
            return_dict=True
        )
    else:
        output = model(
            inputs_embeds=input_embeds,
            attention_mask=input_attention_mask,
            return_dict=True
        )
    return F.softmax(output.logits[:, -1, :], dim=-1)

def generate_attribution(model, input_ids, decoder_input_ids, attention_mask, prediction_ids, model_type):
    # prediction_ids = generate_output.sequences[0, 1:-1]
    attribution_list = []
    for pred_id in prediction_ids:

        input_embeds = _get_embeddings(input_ids, model, model_type)

        if decoder_input_ids is not None:
          decoder_input_embeds = _get_embeddings(decoder_input_ids, model, model_type)
        else:
          decoder_input_embeds = None

        if 't5' in model_type:
            custom_forward = custom_forward_generative
        if 'bert' in model_type:
            custom_forward = custom_forward_func_seq_cla

        if decoder_input_embeds is None:
            forward_func = partial(custom_forward, decoder_input_embeds=decoder_input_embeds, input_attention_mask=attention_mask, model=model)
            inputs = input_embeds
        else:
            forward_func = partial(custom_forward, input_attention_mask=attention_mask, model=model)
            inputs = tuple([input_embeds, decoder_input_embeds])

        input_x_gradient = InputXGradient(forward_func)
        attribution = input_x_gradient.attribute(inputs, target=pred_id)

        if decoder_input_embeds is not None:
            concat_attribution = torch.cat(attribution, dim=1)
            attribution = concat_attribution
        # print('concat attribution shape', concat_attribution.shape)
        attribution = attribution.squeeze(0)
        # print('attribution after squeeze shape', attribution.shape)
        norm = torch.norm(attribution, dim=1)
        # print('attribution after norm', norm.shape)
        attribution = norm / torch.sum(norm)  # Normalize the values so they add up to 1
        # print('attribution after normamlize dividing shape', attribution.shape)
        attribution_list.append(attribution.cpu().detach().numpy())

        if decoder_input_embeds is not None:
            assert len(decoder_input_ids.size()) == 2 # will break otherwise
            decoder_input_ids = torch.cat(
                [decoder_input_ids, torch.tensor([[pred_id]], device=DEVICE)],
                dim=-1
            )
        else:
            input_ids = torch.cat(
                [input_ids, torch.tensor([[pred_id]], device=DEVICE)],
                dim=-1
            )
            if getattr(model, '_prepare_attention_mask_for_generation'):
                assert len(input_ids.size()) == 2 # will break otherwise
                pad_token_id = model.config.pad_token_id
                eos_token_id = model.config.eos_token_id
                attention_mask = model._prepare_attention_mask_for_generation(input_ids, pad_token_id, eos_token_id)
    return attribution_list

def attribution_parser(attribution_array, context_tokens, prefix_text, suffix_text, model_type):
    scores = np.mean(attribution_array, axis=0)
    max_scores = np.max(scores)
    max_scores = 1 if max_scores == 0.0 else max_scores
    scores = scores / max_scores

    assert len(context_tokens) == len(scores), (
        f'Gradient: len input_tokens {len(context_tokens)}'
        + f' != len scores {len(scores)}'
    )

    input_list = list(zip(context_tokens, scores))
    word_list = []
    values_list = input_list
    new_values_list = []
    # print('scores', scores)
    # print('input_tokens', context_tokens)
    if 'bert' in model_type:
        token_prefix = ''
        partial_token_prefix = '##'
    if 't5' in model_type:
        token_prefix = "▁"
        partial_token_prefix = ''
    i = 1
    while i < len(values_list):
        end_word = False
        mean_scores = [values_list[i-1][1]]
        new_world = values_list[i-1][0]
        while end_word is False:
            next_word = values_list[i][0]
            next_score = values_list[i][1]
            # if ((' ' or '▁' or '_' or '-' or ':' or ';' or '(' or ')')
            #         not in next_word.includes('▁')):
            if token_prefix != '':
                if token_prefix not in next_word:
                    new_world += next_word
                    mean_scores.append(next_score)
                else:
                    end_word = True
                    new_values_list.append(
                        [new_world.replace(token_prefix, " "), np.mean(mean_scores)]
                    )
                i += 1
                if i == len(values_list):
                    if not end_word:
                        new_values_list.append(
                            [new_world.replace(token_prefix, " "), np.mean(mean_scores)]
                        )
                        end_word = True
                    else:
                        mean_scores = [values_list[i-1][1]]
                        new_world = values_list[i-1][0]
                        new_values_list.append(
                            [new_world.replace(token_prefix, " "), np.mean(mean_scores)]
                        )
            if partial_token_prefix != '':
                if partial_token_prefix in next_word:
                    new_world += next_word
                    mean_scores.append(next_score)
                else:
                    end_word = True
                    new_values_list.append(
                        [new_world.replace(partial_token_prefix, "") + " ", np.mean(mean_scores)]
                    )
                i += 1
                if i == len(values_list):
                    if not end_word:
                        new_values_list.append(
                            [new_world.replace(partial_token_prefix, "") + " ", np.mean(mean_scores)]
                        )
                        end_word = True
                    else:
                        mean_scores = [values_list[i-1][1]]
                        new_world = values_list[i-1][0]
                        new_values_list.append(
                            [new_world.replace(partial_token_prefix, "") + " ", np.mean(mean_scores)]
                        )


    word_list.append(new_values_list)

    gradient_input = word_list
    for i, input_list in enumerate(gradient_input):
        for k, value in enumerate(input_list):
            opacity = np.int(np.ceil(value[1]*5))
            bg_colors = f'bg-blue-{opacity}' if (
                opacity) > 1 else 'bg-white'
            gradient_input[i][k][1] = bg_colors
        gradient_input[i] = [
            dict(
                text=elem[0], color=elem[1]
                ) for elem in gradient_input[i]
        ]
    prefix_gradient_input = [{ 'text': prefix_text, 'color': 'bg-white' }]
    suffix_gradient_input = [{ 'text': suffix_text, 'color': 'bg-white' }]
    gradient_input = [prefix_gradient_input + gradient_input[0] + suffix_gradient_input]
    return gradient_input

def question_and_answering_pipeline(
    model_type,
    model_name,
    input_text,
    question_list,
    model_lang,
    compute_saliency_map
):
    # eliminate multiple spaces and tabs but can be improved 
    input_text = re.sub(" +", ' ', input_text)
    input_text = re.sub("\s*\n\s*(\s*\n\s*)+", '\n\n', input_text)
    input_text = re.sub("\t+|\t ", ' ', input_text)
    input_text = re.sub(" +", ' ', input_text)
    input_text = input_text.lower()

    

    if model_type == 't5-qa':
        if model_lang == 'en':
            print('translating the text...')
            translator = Translator()
            input_text = translator.translate(input_text, src='it', dest='en').text
        print('loading tokenizer...')
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        # encode the entire text
        input_text_ids = tokenizer.encode(
            input_text,
            return_tensors='pt',
            add_special_tokens=True
        )

        # split the long texts into slices
        text_slices = []
        start_slice = 0
        # max length of the slices
        max_lenght = MAX_LENGHT
        print('slicing...')
        for end_slice in range(max_lenght, input_text_ids.shape[1], max_lenght):
            text_slices.append(tokenizer.decode(input_text_ids[0, start_slice:end_slice], skip_special_tokens=True))
            start_slice = end_slice
        text_slices.append(tokenizer.decode(input_text_ids[0,start_slice:], skip_special_tokens=True))
        print('Number of slicing:', len(text_slices))
        print('loading the model...')
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        model.eval()
        model.zero_grad()
        model.to(DEVICE)
        answer_list = []
        for question in question_list:
            print(f'starting answering question: {question}...')
            answer_dict = { 'question': question, 'answers': []}
            for slice_index, text_slice in enumerate(tqdm(text_slices)):
                # if model_lang == 'en':
                #     context_text = translator.translate(text_slice, src='it', dest='en').text
                #     # question = translator.translate(question, src='it', dest='en').text
                # else:
                context_text = text_slice

                context_ids = tokenizer.encode(context_text, truncation=True, max_length=450)
                context_ids_length = len(context_ids)
                context_tokens = tokenizer.convert_ids_to_tokens(context_ids[:-1])
                context = tokenizer.decode(context_ids, skip_special_tokens=True)

                model_input_text = f"question: {question}  context: {context}"
                # print("model input:", model_input_text)
                model_input_ids_len = len(tokenizer.encode(model_input_text))
                # output = model.generate(model_input_text, max_length=500, attribution=['grad_x_input'])
                # print(output)

                input_features = tokenizer(
                    model_input_text,
                    return_tensors='pt',
                    truncation=True,
                    max_length=490,
                )
                decoder_input_ids = torch.tensor([[model.config.decoder_start_token_id]], device=DEVICE)
                input_ids = input_features['input_ids'].to(DEVICE)
                attention_mask = input_features['attention_mask'].to(DEVICE)
                print(f'generating output slice: {slice_index}...')
                start = time.time()
                generate_output = model.generate(
                    input_ids,
                    max_new_tokens=50,
                    return_dict_in_generate=True,
                    output_scores=True,
                )
                prediction_ids = generate_output.sequences[0, 1:-1]
                end = time.time()
                gen_time = round(end-start, 2)
                print(f'it takes {gen_time} seconds')

                if compute_saliency_map:
                    print(f'generating attribution slice: {slice_index}...')
                    start = time.time()
                    attribution_list = generate_attribution(
                        model,
                        input_ids,
                        decoder_input_ids,
                        attention_mask,
                        prediction_ids,
                        model_type
                    )
                    end = time.time()
                    attr_time = round(end - start, 2)
                    print(f'it takes {attr_time} seconds')
                    print(f'attribution takes {round(attr_time/gen_time, 2)} more time than generate')
                    input_attribution = []
                    for score_pred_token in attribution_list:
                        input_attribution.append(
                            score_pred_token[:model_input_ids_len][-context_ids_length:-1] # -1 because input ends with </s>
                        )
                    attribution_array = np.array(input_attribution)

                    prefix_text = ''.join(text_slices[:slice_index])
                    suffix_text = ''.join(text_slices[(slice_index + 1):])
                    gradient_input = attribution_parser(attribution_array, context_tokens, prefix_text, suffix_text, model_type)
                    gradient_input = gradient_input[0]
                else:
                    gradient_input = None
                answer = tokenizer.decode(generate_output.sequences[0], skip_special_tokens=True)
                answer_score = F.softmax(generate_output.scores[0][0], dim=0)[generate_output.sequences[0, 1]].item()
                # return [{ 'question': question, 'answer': answer, 'saliency_map': gradient_input, 'score': answer_score}]
                answer_dict['answers'].append({
                    'text': answer,
                    'saliency_map': gradient_input,
                    'score': answer_score,
                    'slice_index': slice_index,
                    'question': question
                })
            answer_list.append(answer_dict)
        del model
        return answer_list
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
        max_lenght = MAX_LENGHT
        # print('slicing...')
        for end_slice in range(max_lenght, input_text_ids.shape[1], max_lenght):
            text_slices.append(tokenizer.decode(input_text_ids[0, start_slice:end_slice], skip_special_tokens=True))
            start_slice = end_slice
        text_slices.append(tokenizer.decode(input_text_ids[0,start_slice:], skip_special_tokens=True))
        print('Number of slicing:', len(text_slices))

        answer_list = []
        for question in question_list:
            print(f'answering question: {question}')
            answer_dict = { 'question': question, 'answers': []}
            for index, text_slice in enumerate(text_slices):
                qa_input = {
                    'question': question,
                    'context': text_slice,
                }
                output = nlp(qa_input)
                # if answer_dict["score"] > 0.2:
                    # answers.append(f'Answer text slice {index + 1}: {answer_dict["answer"]}, score: {"{:.2f}".format(answer_dict["score"]*100)}%')
                answer_dict['answers'].append({
                    'text': output["answer"],
                    'saliency_map': None,
                    'score': output["score"],
                    'slice_index': index,
                    'question': question
                })
            answer_list.append(answer_dict)
            
        return answer_list


def compute_saliency_map_qa(
    input_text,
    answer_text,
    question,
    slice_index,
    model_type,
    model_name,
    model_lang
):
    input_text = re.sub(" +", ' ', input_text)
    input_text = re.sub("\s*\n\s*(\s*\n\s*)+", '\n\n', input_text)
    input_text = re.sub("\t+|\t ", ' ', input_text)
    input_text = re.sub(" +", ' ', input_text)
    input_text = input_text.lower()
        

    if model_type == 't5-qa':
        if model_lang == 'en':
            print('translating the text...')
            translator = Translator()
            input_text = translator.translate(input_text, src='it', dest='en').text
        print('loading tokenizer...')
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        # encode the entire text
        input_text_ids = tokenizer.encode(
            input_text,
            return_tensors='pt',
            add_special_tokens=True
        )

        # split the long texts into slices
        text_slices = []
        start_slice = 0
        # max length of the slices
        max_lenght = MAX_LENGHT
        print('slicing...')
        for end_slice in range(max_lenght, input_text_ids.shape[1], max_lenght):
            text_slices.append(tokenizer.decode(input_text_ids[0, start_slice:end_slice], skip_special_tokens=True))
            start_slice = end_slice
        text_slices.append(tokenizer.decode(input_text_ids[0,start_slice:], skip_special_tokens=True))

        print('Number of slicing:', len(text_slices))
        print('loading the model...')
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        model.eval()
        model.zero_grad()
        model.to(DEVICE)

        context_text = text_slices[slice_index]

        context_ids = tokenizer.encode(context_text, truncation=True, max_length=450)
        context_ids_length = len(context_ids)
        context_tokens = tokenizer.convert_ids_to_tokens(context_ids[:-1])
        context = tokenizer.decode(context_ids, skip_special_tokens=True)

        model_input_text = f"question: {question}  context: {context}"
        # print("model input:", model_input_text)
        model_input_ids_len = len(tokenizer.encode(model_input_text))
        # output = model.generate(model_input_text, max_length=500, attribution=['grad_x_input'])
        # print(output)

        input_features = tokenizer(
            model_input_text,
            return_tensors='pt',
            truncation=True,
            max_length=490,
        )
        decoder_input_ids = torch.tensor([[model.config.decoder_start_token_id]], device=DEVICE)
        input_ids = input_features['input_ids'].to(DEVICE)
        attention_mask = input_features['attention_mask'].to(DEVICE)
        print(f'generating output slice: {slice_index}...')
        # This works only for T5 models
        pad_id = model.config.pad_token_id
        prediction_ids = [pad_id] + tokenizer.encode(answer_text)
        print(f'generating attribution slice: {slice_index}...')

        attribution_list = generate_attribution(
            model,
            input_ids,
            decoder_input_ids,
            attention_mask,
            prediction_ids,
            model_type
        )

        input_attribution = []
        for score_pred_token in attribution_list:
            input_attribution.append(
                score_pred_token[:model_input_ids_len][-context_ids_length:-1] # -1 because input ends with </s>
            )
        attribution_array = np.array(input_attribution)

        prefix_text = ''.join(text_slices[:slice_index])
        suffix_text = ''.join(text_slices[(slice_index + 1):])
        gradient_input = attribution_parser(attribution_array, context_tokens, prefix_text, suffix_text, model_type)
        gradient_input = gradient_input[0]
        del model
        return gradient_input
    else:
        return None

def compute_saliency_map_dee(
    input_text,
    sentence_text,
    target_text,
    model_type,
    model_name,
    model_lang,
    task
):
    if model_type == 't5-ner':
        model_name = 'data/checkpoints/simplet5-epoch-6-train-loss-0.2724-val-loss-0.1477'
        print('loading tokenizer...')
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        print('loading the model...')
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        model.eval()
        model.zero_grad()
        model.to(DEVICE)
        
        context_text = ': '.join(sentence_text.split(': ')[1:])

        context_ids = tokenizer.encode(context_text, truncation=True, max_length=450)
        context_ids_length = len(context_ids)
        context_tokens = tokenizer.convert_ids_to_tokens(context_ids[:-1])
        context = tokenizer.decode(context_ids, skip_special_tokens=True)

        model_input_text = f"medication: {context}"
        # print("model input:", model_input_text)
        model_input_ids_len = len(tokenizer.encode(model_input_text))

        input_features = tokenizer(
            model_input_text,
            return_tensors='pt'
        )
        decoder_input_ids = torch.tensor([[model.config.decoder_start_token_id]], device=DEVICE)
        input_ids = input_features['input_ids'].to(DEVICE)
        attention_mask = input_features['attention_mask'].to(DEVICE)
        # This works only for T5 models
        pad_id = model.config.pad_token_id
        prediction_ids = [pad_id] + tokenizer.encode(target_text)
        print(f'generating attribution for target: {target_text}...')

        attribution_list = generate_attribution(
            model,
            input_ids,
            decoder_input_ids,
            attention_mask,
            prediction_ids,
            model_type
        )

        input_attribution = []
        for score_pred_token in attribution_list:
            input_attribution.append(
                score_pred_token[:model_input_ids_len][-context_ids_length:-1] # -1 because input ends with </s>
            )
        attribution_array = np.array(input_attribution)

        prefix_text = ''
        suffix_text = ''
        gradient_input = attribution_parser(attribution_array, context_tokens, prefix_text, suffix_text, model_type)
        gradient_input = gradient_input[0]
        del model
        return gradient_input

    if model_type == 'bert-dee':
        ctx_cats = {}
        ctx_cats['Action'] = {'Inzio':0, 'Fine':1, 'Incremento':2, 'Decremento':3, 'Altri cambiamenti':4, 'Unica dose':5, 'Sconociuto':6}
        ctx_cats['Negation'] = {'Si':0, 'No':1}
        ctx_cats['Temporality'] = {'Passato':0,'Presente':1,'Futuro':2,'Sconosciuto':3}
        ctx_cats['Certainty'] = {'Certo':0, 'Ipotetico':1, 'Condizionale':2, 'Sconosciuto':3}
        ctx_cats['Actor'] = {'Medico':0, 'Paziente':1, 'Sconosciuto':2}
        ctx_cats['Disposition'] = {'Disposizione':0,'Nessuna Disposizione':1,'Indeterminato':2}
        print('loading tokenizer...')
        tokenizer = AutoTokenizer.from_pretrained('bert-base-cased')
        print('loading the model...')
        model = AutoModelForSequenceClassification.from_pretrained('data/checkpoints/' + model_name)
        model.eval()
        model.zero_grad()
        model.to(DEVICE)
        
        context_text = sentence_text

        context_ids = tokenizer.encode(context_text, truncation=True, max_length=450)
        context_ids_length = len(context_ids) - 1 # because of the CLS token at the beginning
        context_tokens = tokenizer.convert_ids_to_tokens(context_ids[1:-1])
        context = tokenizer.decode(context_ids, skip_special_tokens=True)

        model_input_text = context
        # print("model input:", model_input_text)
        model_input_ids_len = len(tokenizer.encode(model_input_text))

        input_features = tokenizer(
            model_input_text,
            return_tensors='pt'
        )
        decoder_input_ids = None
        input_ids = input_features['input_ids'].to(DEVICE)
        attention_mask = input_features['attention_mask'].to(DEVICE)
        print(f'generating attribution for target: {target_text}...')
        target = ctx_cats[task[0].upper() + task[1:]][target_text[0].upper() + target_text[1:]]
        prediction_ids = [target]
        attribution_list = generate_attribution(
            model,
            input_ids,
            decoder_input_ids,
            attention_mask,
            prediction_ids,
            model_type
        )

        input_attribution = []
        for score_pred_token in attribution_list:
            input_attribution.append(
                score_pred_token[:model_input_ids_len][-context_ids_length:-1] # -1 because input ends with </s>
            )
        attribution_array = np.array(input_attribution)

        prefix_text = ''
        suffix_text = ''
        gradient_input = attribution_parser(attribution_array, context_tokens, prefix_text, suffix_text, model_type)
        gradient_input = gradient_input[0]
        del model
        return gradient_input


class Predictor:
    def __init__(self) -> None:
        self.nlp = spacy.load("en_core_sci_md")
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
        # eliminate multiple spaces and tabs but can be improved 
        input_text = re.sub(" +", ' ', input_text)
        input_text = re.sub("\s*\n\s*(\s*\n\s*)+", '\n\n', input_text)
        input_text = re.sub("\t+|\t ", ' ', input_text)
        input_text = re.sub(" +", ' ', input_text)
        text_filtered = input_text.lower() # uncase the text
        # print(text_filtered)
        attribute = 'medications: '
        # input_text = bos + text_filtered + sep + attribute
        input_text_ids = self.tokenizer.encode(
            text_filtered,
            return_tensors='pt',
            add_special_tokens=True
        )
        # print('fino a qui tutto bene init')
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
        doc = self.nlp(input_text)
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