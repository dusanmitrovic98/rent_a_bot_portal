from flask import Flask, request
import requests

app = Flask(__name__)

# Proxy configuration
SERVICES = {
    "dashboard": "http://localhost:5000",
    "ask": "http://localhost:5001"
}

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    # Route to dashboard service
    if path.startswith('dashboard'):
        return proxy_request('dashboard', path)
    
    # Route to ask service
    elif path.startswith('ask'):
        return proxy_request('ask', path)
    
    # Main website
    return "Main Website on Port 8080"

def proxy_request(service, path):
    service_url = f"{SERVICES[service]}/{path.replace(service + '/', '')}"
    resp = requests.request(
        method=request.method,
        url=service_url,
        headers={key: value for key, value in request.headers if key != 'Host'},
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False
    )
    
    # Exclude hop-by-hop headers
    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [
        (name, value) for name, value in resp.raw.headers.items()
        if name.lower() not in excluded_headers
    ]
    
    return (resp.content, resp.status_code, headers)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)