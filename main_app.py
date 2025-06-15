from flask import Flask, request
import os
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return 'Main Flask App Running'

@app.route('/ask-worker')
def ask_worker():
    # Call internal service on localhost:5001
    res = requests.get("http://localhost:5001/ping")
    return f"Worker says: {res.text}"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
