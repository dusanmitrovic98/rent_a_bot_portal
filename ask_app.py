from flask import Flask

app = Flask(__name__)

@app.route('/')
def ask_home():
    return "Ask Service Running on Port 5001"

if __name__ == '__main__':
    app.run(port=5002)