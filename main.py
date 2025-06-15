import os
import importlib.util
import multiprocessing
from flask import Flask, render_template, Blueprint

app = Flask(__name__)

PACKAGE_DIR = os.path.join(os.path.dirname(__file__), 'packages')

# Dynamically register blueprints for each service in packages
def make_service_index():
    def service_index():
        return render_template('index.html')
    return service_index

for service in os.listdir(PACKAGE_DIR):
    service_path = os.path.join(PACKAGE_DIR, service)
    service_template_dir = os.path.join(service_path, 'templates')
    service_index_html = os.path.join(service_template_dir, 'index.html')
    if os.path.isdir(service_path) and os.path.exists(service_index_html):
        bp = Blueprint(
            service,
            __name__ + '_' + service,  # unique name for each blueprint
            template_folder=service_template_dir,
            url_prefix=f'/{service}'
        )
        bp.route('/')(make_service_index())
        app.register_blueprint(bp)

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    processes = []
    # Start each service in its own process
    for service in os.listdir(PACKAGE_DIR):
        service_path = os.path.join(PACKAGE_DIR, service)
        main_py = os.path.join(service_path, 'main.py')
        if os.path.isdir(service_path) and os.path.exists(main_py):
            spec = importlib.util.spec_from_file_location(f"{service}_main", main_py)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            if hasattr(mod, 'run'):
                p = multiprocessing.Process(target=mod.run)
                p.start()
                processes.append(p)
    # Optionally, also run the main portal app in a process
    def run_portal():
        port = int(os.environ.get("PORT", 5000))
        app.run(host='0.0.0.0', port=port)
    p = multiprocessing.Process(target=run_portal)
    p.start()
    processes.append(p)
    for p in processes:
        p.join()
