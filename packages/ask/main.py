from flask import Flask
import json
import os

app = Flask(__name__)

@app.route('/ask')
def ask():
    return 'ask worker is alive!'

with open(os.path.join(os.path.dirname(__file__), 'config.json')) as f:
    config = json.load(f)
port = config.get('port', 5002)

def run():
    app.run(host='127.0.0.1', port=port)
