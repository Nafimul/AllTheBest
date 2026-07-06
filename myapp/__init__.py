import secrets
import os
import uuid
from typing import Any, Dict, List, Optional

from flask import Flask, abort, flash, json, render_template, request
from dotenv import load_dotenv
import httpx
from supabase import create_client

from myapp.db.supabase_category_manager import SupabaseCategoryManager
from myapp.db.supabase_score_manager import SupabaseScoreManager
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
from myapp.models.score import Score
from myapp.models.thing import Thing
from myapp.models.user import User
from myapp.models.vote import Vote


# Return the ordinal suffix for a rank (e.g. 1 -> 'st', 2 -> 'nd', 3 -> 'rd').
def _rank_suffix(rank: int) -> str:
    if 11 <= (rank % 100) <= 13:
        return "th"
    if rank % 10 == 1:
        return "st"
    if rank % 10 == 2:
        return "nd"
    if rank % 10 == 3:
        return "rd"
    return "th"


def _build_spoiler_for_by_thing(scores: list[Score]) -> dict[tuple[str, str], str]:
    """Return a mapping of (thing name, category name) pairs to spoiler labels."""
    spoiler_for_by_thing: dict[tuple[str, str], str] = {}
    for score in scores:
        if score.spoiler_for:
            spoiler_for_by_thing[(score.thing_name, score.category_name)] = (
                score.spoiler_for
            )
    return spoiler_for_by_thing


def build_current_user_votes(votes: list[Vote]) -> dict[str, str]:
    """Return a mapping of category names to the thing currently voted for."""
    return {vote.category_name: vote.thing_name for vote in votes}


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
    score_manager = SupabaseScoreManager(supabase_client)

    def get_current_user_votes():
        current_user_votes = {}
        if current_user.is_authenticated:
            current_user_vote_objects = vote_manager.get_by_user_id(current_user.id)
            current_user_votes = build_current_user_votes(current_user_vote_objects)
        return current_user_votes

    @app.errorhandler(ConnectionError)
    def handle_connection_error(e: ConnectionError):
        if env == "development":
            raise e
        return {"message": "Sorry. Connection issue on our end"}, 503

    @app.errorhandler(404)
    def handle_not_found(error):
        return "404 not found", 404

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
        query = request.args.get("q", "").strip()
        current_user_votes = get_current_user_votes()

        if query:
            matching_categories = category_manager.search_categories_by_name(
                query,
                max_things=10,
                min_similarity=0.1,
            )
            return render_template(
                "categories.html",
                categories_with_scores={},
                current_user_votes=current_user_votes,
                search_query=query,
                search_results=matching_categories,
            )

        THINGS_TO_SHOW_PER_CATEGORY = 3
        categories_with_scores = score_manager.get_categories_with_scores(
            num_scores_per_category=THINGS_TO_SHOW_PER_CATEGORY,
            category_manager=category_manager,
        )
        return render_template(
            "categories.html",
            categories_with_scores=categories_with_scores,
            current_user_votes=current_user_votes,
            search_query=query,
            search_results=[],
        )

    @app.route("/api/search")
    def search() -> tuple[list[dict], int]:
        """Return search suggestions for things or categories."""
        search_type = request.args.get("type", "thing")
        search_text = request.args.get("q", "")

        if search_type == "category":
            categories = category_manager.search_categories_by_name(
                search_text,
                max_things=5,
                min_similarity=0.1,
            )
            return [
                {"name": category.name, "type": "category"} for category in categories
            ], 200

        things = thing_manager.search_things_by_name(
            search_text,
            max_things=5,
            min_similarity=0.1,
        )
        return [{"name": thing.name, "type": "thing"} for thing in things], 200

    @app.route("/api/thing/<string:name>")
    def get_thing_details(name: str) -> tuple[dict, int]:
        """Return existing thing data for autofill."""
        thing = thing_manager.get_thing(name)
        if thing is None:
            return {}, 404

        return {
            "name": thing.name,
            "img_path": thing.img_path,
            "from_thing_names": thing_manager.get_from_thing_names(name),
        }, 200

    @app.route("/api/category/<string:name>")
    def get_category_details(name: str) -> tuple[dict, int]:
        """Return existing category data for autofill."""
        category = category_manager.get(name)
        if category is None:
            return {}, 404

        return {
            "name": category.name,
            "desc": category.desc,
            "is_negative": category.is_negative,
        }, 200

    @app.route("/users")
    def list_users() -> str:
        """Render the categories page with the current users list."""
        profiles = user_manager.get_profiles()
        return render_template(
            "users.html",
            profiles=profiles,
        )

    @app.route("/vote-form")
    # @login_required
    def vote_form() -> str:
        """Render the vote submission form."""
        return render_template("vote-form.html")

    @app.route("/things")
    def list_things() -> str:
        """Render a page with all things or search results."""
        query = request.args.get("q", "").strip()
        if query:
            things = thing_manager.search_things_by_name(
                query,
                max_things=10,
                min_similarity=0.1,
            )
        else:
            things = thing_manager.get_things()

        return render_template(
            "things.html",
            things=things,
            search_query=query,
        )

    @app.route("/categories/<string:name>", methods=["GET"])
    def show_category(name: str) -> str:
        """Render a detailed page for a single category with its leaderboard."""
        category = category_manager.get(name)
        if category is None:
            return render_template("category.html", category=None, scores=[])

        scores = score_manager.get_all()
        # filter and sort scores for this category by votes desc
        scores_for_cat = list(filter(lambda s: s.category_name == name, scores))
        scores_for_cat.sort(key=lambda s: s.num_votes, reverse=True)

        rows = []
        for idx, score in enumerate(scores_for_cat):
            rank = idx + 1
            rows.append(
                {
                    "thing_name": score.thing_name,
                    "num_votes": score.num_votes,
                    "rank_text": f"{rank}{_rank_suffix(rank)}",
                    "spoiler_for": score.spoiler_for,
                }
            )

        current_user_votes = get_current_user_votes()

        first_thing_img_path = None
        if len(rows) > 0:
            first_thing_img_path = thing_manager.get_thing(
                rows[0]["thing_name"]
            ).img_path

        return render_template(
            "category.html",
            category=category,
            scores=rows,
            current_user_votes=current_user_votes,
            first_thing_img_path=first_thing_img_path,
        )

    @app.route("/things/<string:name>", methods=["GET"])
    def show_thing(name: str) -> str:
        """Render a detailed page for a single thing."""
        thing = thing_manager.get_thing(name)
        if thing is None:
            return render_template(
                "thing.html",
                thing=None,
                thing_scores=[],
                current_user_votes={},
            )

        thing_and_descendant_names = thing_manager.get_thing_and_descendant_names(name)
        scores = score_manager.get_by_things(thing_and_descendant_names)

        scores = sorted(scores, key=lambda score: (-score.num_votes))

        current_user_votes = get_current_user_votes()

        from_thing_names = thing_manager.get_from_thing_names(thing.name)
        print(from_thing_names)

        return render_template(
            "thing.html",
            thing=thing,
            thing_scores=scores,
            current_user_votes=current_user_votes,
            from_thing_names=from_thing_names,
        )

    @app.route("/add-things")
    def add_things() -> str:
        """Render the thing submission page."""
        return render_template("add-things.html")

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
        spoiler_for = request.form.get("voteSpoilerFor")
        vote = Vote.from_request(request, current_user.id)
        vote_manager.upsert(vote, spoiler_for)
        return {"message": "Successfully added!"}, 200

    @app.route("/api/vote", methods=["DELETE"])
    @login_required
    def delete_vote() -> tuple[dict, int]:
        """Create or update a vote from request data."""
        vote = Vote.from_request(request, current_user.id)
        vote_manager.delete(vote)
        return {"message": "Successfully deleted!"}, 200

    @app.route("/api/thing", methods=["POST"])
    # @login_required
    def upsert_thing() -> tuple[dict, int]:
        """Create or update a thing with optional image upload."""
        img_file = request.files.get("thingImage")
        thing = Thing.from_request(request)

        thing_manager.upsert_thing(
            thing,
            img_file,
        )
        thing_manager.add_from_things(
            thing.name, request.form.getlist("fromThingNames")
        )
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
            return profile_by_id(current_user.id)

        return render_template(
            "login.html",
        )

    @app.route("/profile/<string:id>", methods=["GET"])
    def profile_by_id(id: str) -> str:
        """Render the current user's profile with their vote history."""
        profile = user_manager.get_profile_by_id(id)
        things_with_votes = score_manager.get_things_with_votes(id)
        current_user_votes = get_current_user_votes()

        return render_template(
            "profile.html",
            profile=profile,
            things_with_votes=things_with_votes,
            current_user_votes=current_user_votes,
        )

    @app.route("/votes/<user_id>/<category_name>/<thing_name>", methods=["GET"])
    def show_vote(user_id: str, category_name: str, thing_name: str) -> str:
        """Render a detailed page for a single vote."""
        vote = vote_manager.get_vote(user_id, category_name, thing_name)
        if vote is None:
            abort(404)

        voter = user_manager.get_profile_by_id(user_id)
        voter_name = voter.name
        thing = thing_manager.get_thing(thing_name)

        # Check if this is a spoiler vote
        spoiler_for_by_thing = _build_spoiler_for_by_thing(score_manager.get_all())
        spoiler_for = spoiler_for_by_thing.get((thing_name, category_name))
        is_spoiler = bool(spoiler_for)

        return render_template(
            "vote.html",
            vote=vote,
            voter_name=voter_name,
            voter_user_id=user_id,
            thing=thing,
            is_spoiler=is_spoiler,
            spoiler_for=spoiler_for,
        )

    return app
