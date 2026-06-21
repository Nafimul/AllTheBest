import secrets
import os
import uuid

from flask import Flask, flash, json, render_template, request
from dotenv import load_dotenv
from supabase import create_client

from myapp.db.supabase_category_manager import SupabaseCategoryManager
from myapp.db.supabase_user_manager import SupabaseUserManager
from myapp.db.supabase_thing_manager import SupabaseThingManager
from myapp.errors.authentication_error import AuthenticationError
from myapp.errors.db_state_error import DbStateError
from myapp.errors.server_error import ServerError
from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user,
    LoginManager,
)
from myapp.models.category import Category
from myapp.models.thing import Thing


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

    supabase_client = create_client(
        os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY")
    )
    user_manager = SupabaseUserManager(supabase_client)
    thing_manager = SupabaseThingManager(supabase_client)
    category_manager = SupabaseCategoryManager(supabase_client)

    @app.route("/")
    def home():
        if os.environ.get("EMAIL"):
            user = user_manager.login(
                os.environ.get("EMAIL"), os.environ.get("PASSWORD")
            )
            login_user(user)

        return render_template("home.html")

    @login_manager.user_loader
    def user_loader(id):
        user = user_manager.get_user()
        return user

    @app.route("/categories")
    def categories():
        try:
            categories = category_manager.get_categories()
            return render_template("categories.html", categories=categories)
        except ServerError:
            return render_template("server-error.html")

    @app.route("/vote-form")
    # @login_required
    def vote_form():
        return render_template("vote-form.html")

    @app.route("/api/category", methods=["POST"])
    # @login_required
    def upsert_category():
        if not request.form.get("categoryName"):
            return {"message": "Missing parameters"}, 400

        try:
            category = Category(
                name=request.form.get("categoryName"),
                is_spoiler=request.form.get("categoryIsSpoiler"),
                desc=request.form.get("categoryDesc"),
                is_negative=request.form.get("categoryIsNegative"),
            )
            category_manager.upsert(category)
            return {"message": "Successfully added!"}, 200
        except DbStateError as e:
            return {"message": "Already exists"}, 400
        except ServerError:
            return {"message": "Server error"}, 500

    @app.route("/api/thing", methods=["POST"])
    # @login_required
    def upsert_thing():
        if not request.form.get("thingName"):
            return {"message": "Missing parameters"}, 400
        try:
            img_file = request.files.get("thingImage")
            img_filename = None
            if img_file:
                img_file.filename += str(
                    uuid.uuid4()
                )  # to avoid name conflicts in storage
                img_filename = img_file.filename
                thing_manager.add_image(img_file)

            thing = Thing.from_request(request, img_filename=img_filename)
            thing_manager.upsert_thing(thing)
            return {"message": "Success!"}, 200
        except ServerError:
            return {"message": "Server error"}, 500

    @app.route("/login", methods=["GET", "POST"])
    def login():
        try:
            if request.method == "POST":
                email = request.form.get("email")
                password = request.form.get("password")
                try:
                    user = user_manager.login(email, password)
                    login_user(user)
                    flash("Logged in successfully")
                    return render_template("home.html")
                except ServerError:
                    flash("Invalid email or password")
                    return render_template("login.html")

            return render_template("login.html")
        except ServerError:
            return render_template("server-error.html")
        except AuthenticationError:
            flash("invalid email or pass")
            return render_template("login.html")

    @app.route("/signup", methods=["POST"])
    def signup():
        try:
            email = request.form.get("email")
            password = request.form.get("password")
            name = request.form.get("name")
            user_manager.signup(email, password, name)
            user_manager.login(email, password)
            flash("Signup successful. You are now logged in.")
            return render_template("signup.html")
        except AuthenticationError:
            flash("email or name taken")
            return render_template("signup.html")
        except ServerError:
            return render_template("server-error.html")

    @app.route("/signup", methods=["GET"])
    def signup_form():
        return render_template("signup.html")

    @app.route("/profile", methods=["GET"])
    def profile():
        return render_template("profile.html", user=current_user)

    return app
