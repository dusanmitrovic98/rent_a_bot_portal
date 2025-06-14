from flask import Flask

app = Flask(__name__)

@app.route('/')
def dashboard_home():
    return "Dashboard Service Running on Port 5000"

if __name__ == '__main__':
    app.run(port=5000)