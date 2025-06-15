from flask import Flask, render_template
import json
import os

app = Flask(__name__)

with open(os.path.join(os.path.dirname(__file__), 'config.json')) as f:
    config = json.load(f)
port = config.get('port', 5001)

@app.route('/')
def dashboard_home():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(host="localhost", port=port)
