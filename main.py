import threading
import os
from flask import Flask, render_template
from dotenv import load_dotenv
from packages.ask import app as ask_app
from packages.dashboard import app as dashboard_app

# Load environment variables from .env file
load_dotenv()

# Main portal app
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

# Optionally, proxy /ask and /dashboard to the respective apps (for local dev)
@app.route('/ask')
def ask_proxy():
    return ask_app.view_functions['ask_home']()

@app.route('/dashboard')
def dashboard_proxy():
    return dashboard_app.view_functions['dashboard_home']()


def run_ask():
    ask_app.run(host="0.0.0.0", port=5002)

def run_dashboard():
    dashboard_app.run(host="0.0.0.0", port=5001)

if __name__ == '__main__':
    # Start ask and dashboard as threads (for local dev)
    threading.Thread(target=run_ask, daemon=True).start()
    threading.Thread(target=run_dashboard, daemon=True).start()
    # Start the portal app on the main thread, using $PORT or 5000
    port = int(os.environ.get('PORT', 5000))
    app.run(host="0.0.0.0", port=port)