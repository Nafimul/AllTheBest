import secrets
import os
import uuid
from typing import Any, Optional

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
from myapp.models.user import User
from myapp.models.vote import Vote


def build_profile_vote_entries(
    votes: list[Vote], thing_manager: Any
) -> list[dict[str, Any]]:
    """Return vote entries sorted with favorite votes first and enriched with thing data."""
    sorted_votes = sorted(votes, key=lambda vote: vote.is_favorite, reverse=True)
    entries = []
    for vote in sorted_votes:
        thing = None
        if thing_manager is not None:
            thing = thing_manager.get_thing(vote.thing_name)
        entries.append({"vote": vote, "thing": thing})
    return entries


def create_app(env: str = "development") -> Flask:
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
    def handle_connection_error(e: ConnectionError):
        if env == "development":
            raise e
        return {"message": "Sorry. Connection issue on our end"}, 503

    @app.errorhandler(Exception)
    def handle_unexpected(e: Exception):
        if env == "development":
            raise e
        return {"message": "Sorry. Something went wrong on our end"}, 500

    @app.route("/")
    def home() -> str:
        """Render the home page."""
        # for auto logging in during development
        if os.environ.get("EMAIL"):
            user = user_manager.login(
                os.environ.get("EMAIL"), os.environ.get("PASSWORD")
            )
            login_user(user)

        return render_template("home.html")

    @login_manager.user_loader
    def user_loader(id: str) -> Optional[User]:
        """Load a user from the authentication backend."""
        return user_manager.get_user()

    @app.route("/categories")
    def list_categories() -> str:
        """Render the categories page with the current category list."""
        THINGS_TO_SHOW_PER_CATEGORY = 3
        categories_with_scores = category_manager.get_categories_with_scores(
            scores_per_category=THINGS_TO_SHOW_PER_CATEGORY
        )
        current_user_votes = []
        if current_user.is_authenticated:
            current_user_vote_objects = vote_manager.get_by_user_id(current_user.id)
            current_user_votes = {
                vote.category_name: vote.thing_name
                for vote in current_user_vote_objects
            }
        return render_template(
            "categories.html",
            categories_with_scores=categories_with_scores,
            current_user_votes=current_user_votes,
        )

    @app.route("/vote-form")
    # @login_required
    def vote_form() -> str:
        """Render the vote submission form."""
        return render_template("vote-form.html")

    @app.route("/api/category", methods=["POST"])
    # @login_required
    def upsert_category() -> tuple[dict, int]:
        """Create or update a category from request data."""
        category = Category.from_request(request)
        category_manager.upsert(category)
        return {"message": "Successfully added!"}, 200

    @app.route("/api/vote", methods=["POST"])
    @login_required
    def upsert_vote() -> tuple[dict, int]:
        """Create or update a vote from request data."""
        vote = Vote.from_request(request, current_user.id)
        vote_manager.upsert(vote)
        return {"message": "Successfully added!"}, 200

    @app.route("/api/thing", methods=["POST"])
    # @login_required
    def upsert_thing() -> tuple[dict, int]:
        """Create or update a thing with optional image upload."""
        img_file = request.files.get("thingImage")
        thing = Thing.from_request(request)
        thing_manager.upsert_thing(thing, img_file)
        return {"message": "Success!"}, 200

    @app.route("/login", methods=["GET", "POST"])
    def login() -> str:
        """Handle login form submission and render results."""
        try:
            email = request.form.get("email")
            password = request.form.get("password")
            user = user_manager.login(email, password)
            login_user(user)

            flash("Logged in successfully")
            return render_template("home.html")
        except (AuthenticationError, TypeError, ValueError) as e:
            flash(str(e))
            return render_template("login.html")

    @app.route("/login", methods=["GET"])
    def login_form():
        return render_template("login.html")

    @app.route("/signup", methods=["POST"])
    def signup() -> str:
        """Handle signup form submission and render the signup page."""
        try:
            email = request.form.get("email")
            password = request.form.get("password")
            name = request.form.get("name")
            user_manager.signup(email, password, name)
            user_manager.login(email, password)
            flash("Signup successful. You are now logged in.")
            return render_template("signup.html")
        except AuthenticationError as e:
            flash(str(e))
            return render_template("signup.html")
        except (TypeError, ValueError) as e:
            flash(str(e))
            return render_template("signup.html")

    @app.route("/signup", methods=["GET"])
    def signup_form():
        return render_template("signup.html")

    @app.route("/profile", methods=["GET"])
    def profile() -> str:
        """Render the current user's profile with their vote history."""
        profile_votes = []
        if current_user.is_authenticated:
            user_votes = vote_manager.get_by_user_id(current_user.id)
            profile_votes = build_profile_vote_entries(user_votes, thing_manager)

        return render_template(
            "profile.html",
            user=current_user,
            profile_votes=profile_votes,
        )

    return app
