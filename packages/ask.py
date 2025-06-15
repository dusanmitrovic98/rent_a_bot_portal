from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def ask_home():
    return render_template('ask.html')

if __name__ == '__main__':
    app.run(port=5002)
