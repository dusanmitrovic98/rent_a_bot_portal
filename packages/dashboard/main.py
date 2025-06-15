import json
import os
from flask import Flask, render_template

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")
try:
    with open(CONFIG_PATH) as f:
        config = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    config = {}

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")


def run():
    static_dir = os.path.join(os.path.dirname(__file__), "..", "..", "static")
    app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=static_dir)

    @app.route("/")
    def home():
        return render_template("index.html", standalone=True)

    port = config.get("port", 5001)
    app.run(host="127.0.0.1", port=port)


if __name__ == "__main__":
    run()
