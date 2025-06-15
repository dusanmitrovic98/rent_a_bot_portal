import multiprocessing
import os
import sys
from flask import Flask, render_template
from dotenv import load_dotenv

def run_flask():
    # Load environment variables from .env file
    load_dotenv()
    app = Flask(__name__)

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/ask')
    def ask_proxy():
        import requests
        try:
            resp = requests.get('http://localhost:5002/')
            return resp.text, resp.status_code, resp.headers.items()
        except Exception as e:
            return f"Ask service unavailable: {e}", 502

    @app.route('/dashboard')
    def dashboard_proxy():
        import requests
        try:
            resp = requests.get('http://localhost:5001/')
            return resp.text, resp.status_code, resp.headers.items()
        except Exception as e:
            return f"Dashboard service unavailable: {e}", 502

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

def run_ask():
    os.system(f'{sys.executable} packages{os.sep}ask{os.sep}main.py')

def run_dashboard():
    os.system(f'{sys.executable} packages{os.sep}dashboard{os.sep}main.py')

if __name__ == '__main__':
    p_ask = multiprocessing.Process(target=run_ask)
    p_dashboard = multiprocessing.Process(target=run_dashboard)
    p_ask.start()
    p_dashboard.start()
    # Give services time to start
    import time
    time.sleep(1)
    run_flask()
    p_ask.join()
    p_dashboard.join()