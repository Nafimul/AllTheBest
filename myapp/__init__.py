import secrets
import os

from flask import Flask, flash, json, render_template, request
from dotenv import load_dotenv

from myapp.db.manager_exception import ManagerException
from flask_login import current_user, login_required, login_user, logout_user, LoginManager
from myapp.db.supabase_postgres_manager import SupabasePostgresManager

def create_app(env="development"):
    load_dotenv()
    app = Flask(__name__)
    app.secret_key = secrets.token_hex(16)  # This is necessary for flash!
    app.config.from_file(f"{env}.json", load=json.load)
    app.config.from_prefixed_env()
    app.app_context().push()

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "login"
    login_manager.login_message = "You must be logged in to do that."

    db_manager = SupabasePostgresManager( os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))

    @app.route("/")
    def home():
        # return [current_user.id, current_user.is_authenticated, current_user.email]
        return render_template("home.html")
    
    @login_manager.user_loader
    def user_loader(id):
        user = db_manager.get_user()
        return user
    
    @app.route("/categories")
    def categories():
        categories = db_manager.get_categories()
        return render_template("categories.html", categories=categories)
    
    @app.route("/add-category")
    def add_category_form():
        return render_template("add-category.html")
    
    @app.route("/category", methods=["POST"])
    def add_category():
        try:
            db_manager.add_category(name=request.form["name"])
            flash("Category added successfully")
        except ManagerException as e:
            flash("Failed to add category")
        return render_template("add-category.html")
    
    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            email = request.form.get("email")
            password = request.form.get("password")
            try:
                user = db_manager.login(email, password)
                login_user(user)
                flash("Logged in successfully")
                return render_template("home.html")
            except ManagerException:
                flash("Invalid email or password")
                return render_template("login.html")

        return render_template("login.html")
    
    @app.route("/profile", methods=["GET"])
    def profile():
        return render_template("profile.html", user = current_user)
    
    return app

    

