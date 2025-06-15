import os
import sys
import signal
import importlib.util
import multiprocessing

from flask import Flask, render_template
from jinja2 import ChoiceLoader, FileSystemLoader, PrefixLoader

BASE_DIR = os.path.dirname(__file__)
PACKAGE_DIR = os.path.join(BASE_DIR, "packages")
MAIN_TEMPLATES = os.path.join(BASE_DIR, "templates")

app = Flask(__name__, static_folder="static")


def discover_packages(package_dir):
    """Discover package template loaders and service packages."""
    template_loaders = {}
    service_pkgs = []
    for pkg_name in os.listdir(package_dir):
        pkg_path = os.path.join(package_dir, pkg_name)
        if not os.path.isdir(pkg_path):
            continue
        templates_path = os.path.join(pkg_path, "templates")
        main_py_path = os.path.join(pkg_path, "main.py")
        if os.path.isdir(templates_path):
            template_loaders[pkg_name] = FileSystemLoader(templates_path)
        if os.path.isfile(main_py_path):
            service_pkgs.append((pkg_name, pkg_path))
    return template_loaders, service_pkgs


package_template_loaders, service_packages = discover_packages(PACKAGE_DIR)

app.jinja_loader = ChoiceLoader(
    [
        FileSystemLoader(MAIN_TEMPLATES),
        PrefixLoader(package_template_loaders, delimiter=":"),
    ]
)


@app.route("/")
def home() -> str:
    """Render the main index page."""
    return render_template("index.html")


def create_package_view(pkg_name: str):
    """Return a view function for a package's index page."""

    def view():
        return render_template(f"{pkg_name}:index.html", standalone=False)

    return view


for pkg in package_template_loaders:
    app.add_url_rule(
        f"/{pkg}",
        endpoint=f"{pkg}_home",
        view_func=create_package_view(pkg),
        strict_slashes=False,
    )


def run_service(service_path: str) -> None:
    """Run a service module with proper error handling."""
    main_py = os.path.join(service_path, "main.py")
    module_name = f"service_{os.path.basename(service_path)}"
    try:
        spec = importlib.util.spec_from_file_location(module_name, main_py)
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            if hasattr(mod, "run"):
                mod.run()
            else:
                print(f"No 'run' function in {main_py}")
        else:
            print(f"Could not load module from {main_py}")
    except Exception as e:
        print(f"Service {service_path} failed: {str(e)}")
        import traceback

        traceback.print_exc()


def shutdown(processes):
    """Graceful shutdown handler."""
    for p in processes:
        p.terminate()
        p.join()
    sys.exit(0)


def start_service_processes(service_packages):
    """Start all service package processes and return the process list."""
    return [
        multiprocessing.Process(
            target=run_service, args=(pkg_dir,), name=f"Service-{pkg}"
        )
        for pkg, pkg_dir in service_packages
    ]


def register_signal_handlers(processes):
    """Register signal handlers for graceful shutdown."""

    def shutdown_handler(signum, frame):
        shutdown(processes)

    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, shutdown_handler)


def main():
    processes = start_service_processes(service_packages)
    for p in processes:
        p.start()
    register_signal_handlers(processes)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
