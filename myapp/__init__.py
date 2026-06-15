import secrets
import os

from flask import Flask, flash, json, render_template, request
from dotenv import load_dotenv

from myapp.errors.db_state_error import DbStateError
from myapp.errors.server_error import ServerError
from flask_login import current_user, login_required, login_user, logout_user, LoginManager
from myapp.db.supabase_postgres_manager import SupabasePostgresManager
from myapp.models.category import Category

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
        if (os.environ.get("EMAIL")):
            user = db_manager.login(os.environ.get("EMAIL"), os.environ.get("PASSWORD"))
            login_user(user)

        return render_template("home.html")
    
    @login_manager.user_loader
    def user_loader(id):
        user = db_manager.get_user()
        return user
    
    @app.route("/categories")
    def categories():
        try:
            categories = db_manager.get_categories()
            return render_template("categories.html", categories=categories)
        except ServerError:
            return render_template("server-error.html")
    
    @app.route("/add-category")
    @login_required
    def add_category_form():
        return render_template("add-category.html")
    
    @app.route("/api/category", methods=["POST"])
    @login_required
    def add_category():
        if request.form["name"]:
            category = Category(name=request.form["name"])
        else:
            return {"message": "Missing parameters"}, 400
        try:
            db_manager.add_category(category)
            return {"message": "Successfully added!"}, 200
        except DbStateError as e:
            return {"message": "Already exists"}, 400
        except ServerError:
            return {"message": "Server error"}, 500

    @app.route("/login", methods=["GET", "POST"])
    def login():
        try:
            if request.method == "POST":
                email = request.form.get("email")
                password = request.form.get("password")
                try:
                    user = db_manager.login(email, password)
                    login_user(user)
                    flash("Logged in successfully")
                    return render_template("home.html")
                except ServerError:
                    flash("Invalid email or password")
                    return render_template("login.html")
                
            return render_template("login.html")
        except ServerError:
            return render_template("server-error.html")
    
    @app.route("/signup", methods=["GET", "POST"])
    def signup():
        try:
            if request.method == "POST":
                email = request.form.get("email")
                password = request.form.get("password")
                name = request.form.get("name")
                try:
                    db_manager.signup(email, password, name)
                    db_manager.login(email, password)
                    flash("Signup successful, please log in")
                except ServerError:
                    flash("Signup failed")

            return render_template("signup.html")
        except ServerError:
            return render_template("server-error.html")
    
    @app.route("/profile", methods=["GET"])
    def profile():
        return render_template("profile.html", user = current_user)
    
    return app

    

