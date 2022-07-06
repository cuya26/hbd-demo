from flask import Flask, request, jsonify
from flask_cors import CORS
from os import path
import json
from model import Predictor


app = Flask(__name__)
CORS(app)
pred = Predictor()


@app.route('/discharge_letters', methods=['GET'])
def discharge_letters():
    if request.method == 'GET':
        if path.isfile('data/discharge_letters.json'):
            with open('data/discharge_letters.json') as f:
                return jsonify(json.load(f))
        else:
            return jsonify({})

@app.route('/extract_data_table', methods=['POST'])
def extract_data_table():
    if request.method == 'POST':
        input_text = request.get_json()['input_text']
        data_list = pred.inference(input_text)
        return jsonify(data_list)


if __name__ == '__main__':
    app.run()
