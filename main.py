import os
import importlib.util
import multiprocessing
from flask import Flask, render_template
from jinja2 import ChoiceLoader, FileSystemLoader

app = Flask(__name__)

PACKAGE_DIR = os.path.join(os.path.dirname(__file__), 'packages')

# Dynamically add all package template folders to Jinja loader
extra_template_folders = [os.path.join(PACKAGE_DIR, pkg, 'templates')
    for pkg in os.listdir(PACKAGE_DIR)
    if os.path.isdir(os.path.join(PACKAGE_DIR, pkg, 'templates'))]

# Always include the main templates folder
main_templates = os.path.join(os.path.dirname(__file__), 'templates')
app.jinja_loader = ChoiceLoader([
    FileSystemLoader([main_templates] + extra_template_folders)
])

@app.route('/')
def home():
    return render_template('index.html')

# Dynamically create a route for each package that has a templates/index.html
for pkg in os.listdir(PACKAGE_DIR):
    template_path = os.path.join(PACKAGE_DIR, pkg, 'templates', 'index.html')
    if os.path.exists(template_path):
        route = f'/{pkg}'
        def make_view(pkg_name):
            def view():
                # Render the correct index.html for the package by referencing it as 'index.html' (since it's in the extra_template_folders)
                return render_template('index.html')
            return view
        app.add_url_rule(route, f'{pkg}_index', make_view(pkg))

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
