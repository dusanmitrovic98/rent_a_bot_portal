from flask import Flask, request, render_template
import requests
import os
from dotenv import load_dotenv

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()

# Proxy configuration
# Map service names to their actual ports
SERVICE_PORTS = {
    'dashboard': 5001,
    'ask': 5002,
}
SERVICES = {name: f"http://localhost:{port}" for name, port in SERVICE_PORTS.items()}

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
    port = int(os.environ.get('PORT', 5000))
    app.run(host="0.0.0.0", port=port)