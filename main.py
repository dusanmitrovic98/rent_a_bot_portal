import os
import multiprocessing
import signal
import sys
import traceback
from flask import Flask, render_template
from jinja2 import ChoiceLoader, FileSystemLoader, PrefixLoader

app = Flask(__name__)

PACKAGE_DIR = os.path.join(os.path.dirname(__file__), 'packages')
main_templates = os.path.join(os.path.dirname(__file__), 'templates')

# Configure template loaders with namespacing
package_loaders = {}
for pkg in os.listdir(PACKAGE_DIR):
    pkg_dir = os.path.join(PACKAGE_DIR, pkg)
    template_dir = os.path.join(pkg_dir, 'templates')
    
    if os.path.isdir(template_dir):
        # Namespace package templates under package name
        package_loaders[pkg] = FileSystemLoader(template_dir)

# Create loader hierarchy
app.jinja_loader = ChoiceLoader([
    FileSystemLoader(main_templates),  # Main templates
    PrefixLoader(package_loaders, delimiter=':')  # Package templates under package namespace
])

@app.route('/')
def home():
    return render_template('index.html')

# Register package routes with unique endpoint names
for pkg in package_loaders:
    def create_package_view(pkg_name):
        def view():
            return render_template(f'{pkg_name}:index.html')  # Use namespaced template
        return view
        
    view_func = create_package_view(pkg)
    endpoint_name = f'{pkg}_home'  # Unique endpoint per package
    app.add_url_rule(f'/{pkg}', endpoint=endpoint_name, view_func=view_func, strict_slashes=False)

def run_service(service_path):
    """Run a service module with proper error handling"""
    sys.path.insert(0, service_path)
    try:
        from main import run  # Dynamic import
        run()
    except Exception as e:
        print(f"Service {service_path} failed: {str(e)}")
        traceback.print_exc()

def shutdown(signum, frame):
    """Graceful shutdown handler"""
    for p in processes:
        p.terminate()
    sys.exit(0)

if __name__ == '__main__':
    processes = []
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    # Start package services
    for pkg in os.listdir(PACKAGE_DIR):
        pkg_dir = os.path.join(PACKAGE_DIR, pkg)
        if os.path.exists(os.path.join(pkg_dir, 'main.py')):
            p = multiprocessing.Process(
                target=run_service,
                args=(pkg_dir,),
                name=f"Service-{pkg}"
            )
            p.start()
            processes.append(p)

    # Run portal in main process
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)