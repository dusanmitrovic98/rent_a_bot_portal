import multiprocessing
import os
import sys
import subprocess
import time

def start_ask():
    subprocess.run([sys.executable, os.path.join('packages', 'ask', 'main.py')])

def start_dashboard():
    subprocess.run([sys.executable, os.path.join('packages', 'dashboard', 'main.py')])

def start_portal():
    subprocess.run([sys.executable, 'main.py'])

if __name__ == "__main__":
    p_ask = multiprocessing.Process(target=start_ask)
    p_dashboard = multiprocessing.Process(target=start_dashboard)
    p_portal = multiprocessing.Process(target=start_portal)

    p_ask.start()
    p_dashboard.start()
    time.sleep(1)  # Give services time to start
    p_portal.start()

    p_ask.join()
    p_dashboard.join()
    p_portal.join()
