import secrets

from flask import Flask, json, render_template


def create_app(env="development"):
    app = Flask(__name__)
    app.secret_key = secrets.token_hex(16)  # This is necessary for flash!
    app.config.from_file(f"{env}.json", load=json.load)
    app.config.from_prefixed_env()
    app.app_context().push()

    @app.route("/")
    def home():
        return render_template("home.html")
    
    @app.route("/categories")
    def categories():
        return render_template("categories.html")
    
    return app