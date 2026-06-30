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


# Return the 1-based rank of the given score within its category score list.
def _resolve_category_rank(score: Score, category_scores: list[Score]) -> int:
    return next(
        (
            index + 1
            for index, item in enumerate(category_scores)
            if item.thing_name == score.thing_name
        ),
        len(category_scores),
    )


def _build_spoiler_for_by_thing(scores: list[Score]) -> dict[str, str]:
    """Return a mapping of thing names to spoiler labels for marked scores."""
    spoiler_for_by_thing: dict[str, str] = {}
    for score in scores:
        if score.spoiler_for:
            spoiler_for_by_thing[score.thing_name] = score.spoiler_for
    return spoiler_for_by_thing


# Build a list of score rows for a thing, sorted with first-place categories first.
# name: thing name to filter on, scores: all category scores.
def _build_thing_scores(name: str, scores: list[Score]) -> list[dict[str, Any]]:
    categories_by_name: dict[str, list[Score]] = {}
    for score in scores:
        categories_by_name.setdefault(score.category_name, []).append(score)

    thing_scores: list[dict[str, Any]] = []
    for score in filter(lambda s: s.thing_name == name, scores):
        category_scores = sorted(
            categories_by_name[score.category_name],
            key=lambda item: item.num_votes,
            reverse=True,
        )
        rank = _resolve_category_rank(score, category_scores)
        thing_scores.append(
            {
                "category_name": score.category_name,
                "num_votes": score.num_votes,
                "rank_text": f"{rank}{_rank_suffix(rank)}",
                "is_first": rank == 1,
            }
        )

    return sorted(
        thing_scores, key=lambda row: (0 if row["is_first"] else 1, -row["num_votes"])
    )


def build_profile_vote_entries(
    votes: list[Vote],
    thing_manager: Any,
    spoiler_for_by_thing: Optional[dict[str, str]] = None,
) -> list[dict[str, Any]]:
    """Return vote entries sorted with favorite votes first and enriched with thing data."""
    sorted_votes = sorted(votes, key=lambda vote: vote.is_favorite, reverse=True)
    entries = []
    spoiler_lookup = spoiler_for_by_thing or {}
    for vote in sorted_votes:
        thing = None
        if thing_manager is not None:
            thing = thing_manager.get_thing(vote.thing_name)
        spoiler_for = spoiler_lookup.get(vote.thing_name)
        entries.append(
            {
                "vote": vote,
                "thing": thing,
                "spoiler_for": spoiler_for,
                "is_spoiler": bool(spoiler_for),
            }
        )
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

    @app.route("/things")
    def list_things() -> str:
        """Render a page with all things."""
        things = thing_manager.get_things()
        return render_template("things.html", things=things)

    @app.route("/categories/<string:name>", methods=["GET"])
    def show_category(name: str) -> str:
        """Render a detailed page for a single category with its leaderboard."""
        category = category_manager.get(name)
        if category is None:
            return render_template("category.html", category=None, scores=[])

        scores = category_manager.get_scores()
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

        current_user_votes = {}
        if current_user.is_authenticated:
            current_user_vote_objects = vote_manager.get_by_user_id(current_user.id)
            current_user_votes = {
                vote.category_name: vote.thing_name
                for vote in current_user_vote_objects
            }

        return render_template(
            "category.html",
            category=category,
            scores=rows,
            current_user_votes=current_user_votes,
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

        scores = category_manager.get_scores()
        thing_scores = _build_thing_scores(name, scores)

        current_user_votes = {}
        if current_user.is_authenticated:
            current_user_vote_objects = vote_manager.get_by_user_id(current_user.id)
            current_user_votes = {
                vote.category_name: vote.thing_name
                for vote in current_user_vote_objects
            }

        return render_template(
            "thing.html",
            thing=thing,
            thing_scores=thing_scores,
            current_user_votes=current_user_votes,
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
            return profile_by_id(current_user.id)

        return render_template(
            "login.html",
        )

    @app.route("/profile/<string:id>", methods=["GET"])
    def profile_by_id(id: str) -> str:
        """Render the current user's profile with their vote history."""
        user = user_manager.get_profile_by_id(id)
        user_votes = vote_manager.get_by_user_id(id)

        spoiler_for_by_thing = _build_spoiler_for_by_thing(
            category_manager.get_scores()
        )

        profile_votes = []
        profile_votes = build_profile_vote_entries(
            user_votes,
            thing_manager,
            spoiler_for_by_thing=spoiler_for_by_thing,
        )

        return render_template(
            "profile.html",
            user=user,
            profile_votes=profile_votes,
        )

    @app.route("/votes/<user_id>/<category_name>/<thing_name>", methods=["GET"])
    def show_vote(user_id: str, category_name: str, thing_name: str) -> str:
        """Render a detailed page for a single vote."""
        vote = vote_manager.get_vote(user_id, category_name, thing_name)

        if vote is None:
            return render_template("vote.html", vote=None)

        # Get voter information
        voter_name = "Unknown User"
        try:
            voter = user_manager.get_profile_by_id(user_id)
            if voter:
                voter_name = voter.name
        except ConnectionError:
            pass

        # Get thing information
        thing = None
        try:
            thing = thing_manager.get_thing(thing_name)
        except ConnectionError:
            pass

        # Check if this is a spoiler vote
        spoiler_for_by_thing = _build_spoiler_for_by_thing(
            category_manager.get_scores()
        )
        spoiler_for = spoiler_for_by_thing.get(thing_name)
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
