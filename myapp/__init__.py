import secrets
import os
import uuid

from flask import Flask, flash, json, render_template, request
from dotenv import load_dotenv
import httpx
from supabase import create_client

from myapp.db.supabase_category_manager import SupabaseCategoryManager
from myapp.db.supabase_user_manager import SupabaseUserManager
from myapp.db.supabase_thing_manager import SupabaseThingManager
from myapp.db.supabase_vote_manager import SupabaseVoteManager
from myapp.errors.authentication_error import AuthenticationError
from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user,
    LoginManager,
)
from myapp.models.category import Category
from myapp.models.thing import Thing
from myapp.models.vote import Vote


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
    vote_manager = SupabaseVoteManager(supabase_client)

    @app.errorhandler(ConnectionError)
    def handle_connection_error(e):
        return {"message": "Sorry. Connection issue on our end"}, 503

    @app.errorhandler(Exception)
    def handle_unexpected(e):
        app.logger.exception(e)
        return {"message": "Sorry. Something went wrong on our end"}, 500

    @app.route("/")
    def home():
        # for auto logging in during development
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
    def list_categories():
        categories = category_manager.get_categories()
        return render_template("categories.html", categories=categories)

    @app.route("/vote-form")
    # @login_required
    def vote_form():
        return render_template("vote-form.html")

    @app.route("/api/category", methods=["POST"])
    # @login_required
    def upsert_category():
        if not request.form.get("categoryName"):
            return {"message": "Missing parameters"}, 400

        category = Category.from_request(request)
        category_manager.upsert(category)
        return {"message": "Successfully added!"}, 200

    @app.route("/api/vote", methods=["POST"])
    @login_required
    def upsert_vote():
        if not request.form.get("categoryName") or not request.form.get("thingName"):
            return {"message": "Missing parameters"}, 400

        vote = Vote.from_request(request, current_user.id)
        vote_manager.upsert(vote)
        return {"message": "Successfully added!"}, 200

    @app.route("/api/thing", methods=["POST"])
    # @login_required
    def upsert_thing():
        if not request.form.get("thingName"):
            return {"message": "Missing parameters"}, 400

        img_file = request.files.get("thingImage")
        thing = Thing.from_request(request)
        thing_manager.upsert_thing(thing, img_file)
        return {"message": "Success!"}, 200

    @app.route("/login", methods=["GET", "POST"])
    def login():
        try:
            email = request.form.get("email")
            password = request.form.get("password")
            user = user_manager.login(email, password)
            login_user(user)

            flash("Logged in successfully")
            return render_template("home.html")
        except AuthenticationError:
            flash("invalid email or pass")
            return render_template("login.html")

    @app.route("/login", methods=["GET"])
    def login_form():
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

    @app.route("/signup", methods=["GET"])
    def signup_form():
        return render_template("signup.html")

    @app.route("/profile", methods=["GET"])
    def profile():
        return render_template("profile.html", user=current_user)

    return app
