from flask import Flask

worker_app = Flask(__name__)

@worker_app.route('/ping')
def ping():
    return 'pong from worker'

def start_worker():
    worker_app.run(host='127.0.0.1', port=5001)
