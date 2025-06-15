import multiprocessing
from main import app
# Update the import path below if 'ask.py' is in a different location
from packages.ask import run as ask_run
import os

def start_main():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    targets = [ask_run, start_main]
    processes = [multiprocessing.Process(target=target) for target in targets]

    for p in processes:
        p.start()

    for p in processes:
        p.join()
