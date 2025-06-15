import os
import importlib
from flask import Flask, render_template, abort
import multiprocessing

app = Flask(__name__, template_folder=None)

# Dynamically register blueprints for each service in packages
PACKAGE_DIR = os.path.join(os.path.dirname(__file__), 'packages')

for service in os.listdir(PACKAGE_DIR):
    service_path = os.path.join(PACKAGE_DIR, service)
    if os.path.isdir(service_path):
        main_py = os.path.join(service_path, 'main.py')
        service_template_dir = os.path.join(service_path, 'templates')
        service_index_html = os.path.join(service_template_dir, 'index.html')
        if os.path.exists(main_py) and os.path.exists(service_index_html):
            # Import the service's main.py as a module
            spec = importlib.util.spec_from_file_location(f"{service}_main", main_py)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            # Register a route for the service
            def make_service_page(service=service, template_dir=service_template_dir):
                def service_page():
                    return render_template(os.path.join(template_dir, 'index.html'))
                return service_page
            app.add_url_rule(f'/{service}', f'{service}_page', make_service_page())

@app.route('/')
def home():
    return render_template(os.path.join('..', 'templates', 'index.html'))

@app.route('/<service>')
def service_auto_route(service):
    service_template = os.path.join(PACKAGE_DIR, service, 'templates', 'index.html')
    if os.path.exists(service_template):
        # Flask expects template paths relative to a templates folder, so use absolute path
        return render_template(service_template)
    abort(404)

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
