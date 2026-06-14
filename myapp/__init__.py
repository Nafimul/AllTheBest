import secrets
import os

from flask import Flask, flash, json, render_template, request
from dotenv import load_dotenv

from myapp.db.manager_exception import ManagerException
from myapp.db.supabase_postgres_manager import SupabasePostgresManager

def create_app(env="development"):
    load_dotenv()
    app = Flask(__name__)
    app.secret_key = secrets.token_hex(16)  # This is necessary for flash!
    app.config.from_file(f"{env}.json", load=json.load)
    app.config.from_prefixed_env()
    app.app_context().push()

    db_manager = SupabasePostgresManager( os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))

    @app.route("/")
    def home():
        return render_template("home.html")
    
    @app.route("/categories")
    def categories():
        categories = db_manager.get_categories()
        return render_template("categories.html", categories=categories)
    
    @app.route("/add-category")
    def add_category():
        return render_template("add-category.html")
    
    @app.route("/category", methods=["POST"])
    def add_category():
        try:
            db_manager.add_category(name=request.form["name"])
            flash("Category added successfully")
        except ManagerException as e:
            flash("Failed to add category")
        return render_template("add-category.html")
    
    return app