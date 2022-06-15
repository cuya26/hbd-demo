from flask import Flask, request, jsonify
from flask_cors import CORS


app = Flask(__name__)
CORS(app)


@app.route('/', methods=['GET'])
def init():
    return "init backend"


if __name__ == '__main__':
    app.run()
