from flask import Flask, request, render_template
import requests
import os
from dotenv import load_dotenv
import json
import subprocess
import sys
import signal
import atexit

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()

# Proxy configuration
# Dynamically load service ports from each service's config.json
SERVICE_PORTS = {}
SERVICES = {}
services_dir = os.path.join(os.path.dirname(__file__), 'packages')
for service_name in os.listdir(services_dir):
    service_path = os.path.join(services_dir, service_name)
    config_path = os.path.join(service_path, 'config.json')
    if os.path.isdir(service_path) and os.path.isfile(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
            port = config.get('port')
            if port:
                SERVICE_PORTS[service_name] = port
                SERVICES[service_name] = f"http://localhost:{port}"

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    # Dynamically check for service in SERVICES
    for service in SERVICES:
        if path == service or path.startswith(service + '/'):
            return proxy_request(service, path)
    # Main website
    return render_template('index.html')

def proxy_request(service, path):
    # Remove the service prefix from the path robustly
    prefix = service + '/'
    forward_path = path[len(prefix):] if path.startswith(prefix) else ''
    # Build the full URL, including query string if present
    service_url = f"{SERVICES[service]}/" + forward_path
    if request.query_string:
        service_url += '?' + request.query_string.decode()
    # Forward all headers except Host
    headers = {key: value for key, value in request.headers if key.lower() != 'host'}
    resp = requests.request(
        method=request.method,
        url=service_url,
        headers=headers,
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False,
        stream=True
    )
    # Exclude hop-by-hop headers
    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    response_headers = [
        (name, value) for name, value in resp.headers.items()
        if name.lower() not in excluded_headers
    ]
    return (resp.content, resp.status_code, response_headers)

if __name__ == '__main__':
    # Start all services as subprocesses
    service_processes = []
    for service_name in SERVICES:
        service_main_py = os.path.join(services_dir, service_name, 'main.py')
        if os.path.isfile(service_main_py):
            proc = subprocess.Popen([sys.executable, service_main_py])
            service_processes.append(proc)

    def cleanup_services(*args):
        for proc in service_processes:
            if proc.poll() is None:
                try:
                    proc.terminate()
                except Exception:
                    pass
        # Give them a moment to terminate, then force kill if needed
        for proc in service_processes:
            try:
                proc.wait(timeout=3)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass

    # Register cleanup on exit and signals
    atexit.register(cleanup_services)
    signal.signal(signal.SIGINT, lambda sig, frame: (cleanup_services(), exit(0)))
    signal.signal(signal.SIGTERM, lambda sig, frame: (cleanup_services(), exit(0)))

    port = int(os.environ.get('PORT', 5000))
    app.run(host="0.0.0.0", port=port)