from flask import Flask, request, jsonify
from flask_cors import CORS
from os import path
import json
from model import Predictor, question_and_answering_pipeline


app = Flask(__name__)
CORS(app)
pred = Predictor()


# @app.route('/discharge_letters', methods=['GET'])
# def discharge_letters():
#     if request.method == 'GET':
#         if path.isfile('data/discharge_letters.json'):
#             with open('data/discharge_letters.json') as f:
#                 return jsonify(json.load(f))
#         else:
#             return jsonify({})

@app.route('/extract_data_table', methods=['POST'])
def extract_data_table():
    if request.method == 'POST':
        input_text = request.get_json()['input_text']
        data_list = pred.inference(input_text)
        return jsonify(data_list)

@app.route('/answer_question', methods=['POST'])
def answer_question():
    if request.method == 'POST':
        input_text = request.get_json()['input_text']
        question = request.get_json()['question']
        answer_list = question_and_answering_pipeline(input_text, [question])
        return jsonify(answer_list[0]['answer'])

@app.route('/answer_question_list', methods=['POST'])
def answer_question_list():
    if request.method == 'POST':
        input_text = request.get_json()['input_text']
        question_answer_list = request.get_json()['question_answer_list']
        question_list = [element['question'] for element in question_answer_list]
        return jsonify(question_and_answering_pipeline(input_text, question_list))


if __name__ == '__main__':
    app.run()
