import multiprocessing
from main_app import app
from service_worker import start_worker
import os

def start_main():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    p1 = multiprocessing.Process(target=start_worker)
    p2 = multiprocessing.Process(target=start_main)
    
    p1.start()
    p2.start()
    
    p1.join()
    p2.join()
