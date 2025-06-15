import threading
import os
import subprocess
import sys
import time
from flask import Flask, render_template
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Main portal app
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

if __name__ == '__main__':
    # Start ask and dashboard as subprocesses (like your old project)
    ask_proc = subprocess.Popen([sys.executable, os.path.join('packages', 'ask', 'main.py')])
    dashboard_proc = subprocess.Popen([sys.executable, os.path.join('packages', 'dashboard', 'main.py')])
    try:
        time.sleep(1)  # Give services time to start
        def run_flask():
            port = int(os.environ.get("PORT", 5000))
            app.run(host="0.0.0.0", port=port)
        threading.Thread(target=run_flask, daemon=True).start()
    finally:
        # Cleanup: terminate subprocesses on exit
        ask_proc.terminate()
        dashboard_proc.terminate()
        ask_proc.wait()
        dashboard_proc.wait()