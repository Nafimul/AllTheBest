from typing import Any, Dict, List, Optional
import httpx

from myapp.models.category import Category
from myapp.models.score import Score
from myapp.models.vote import Vote


class SupabaseScoreManager:
    def __init__(self, supabase: Any) -> None:
        """Manage category CRUD operations in Supabase."""
        self.supabase = supabase

    def get_all(self) -> List[Score]:
        """Return all scores stored in Supabase."""
        try:
            response = self.supabase.table("scores").select("*").execute()
            scores = []
            for item in response.data:
                scores.append(Score.from_json(item))
            return scores
        except httpx.HTTPError as e:
            raise ConnectionError(str(e)) from e

    def get_by_thing(self, thing_name) -> List[Score]:
        """Return score with given thing_name."""
        try:
            response = (
                self.supabase.table("scores")
                .select("*")
                .filter("thing_name", "eq", thing_name)
                .execute()
            )
            items = []
            for item in response.data:
                items.append(Score.from_json(item))
            return items
        except httpx.HTTPError as e:
            raise ConnectionError(str(e)) from e

    def get_by_things(self, thing_names: List[str]) -> List[Score]:
        try:
            response = (
                self.supabase.table("scores")
                .select("*")
                .in_("thing_name", thing_names)
                .execute()
            )
            items = []
            for item in response.data:
                items.append(Score.from_json(item))
            return items
        except httpx.HTTPError as e:
            raise ConnectionError(str(e)) from e

    def get_categories_with_scores(
        self, num_scores_per_category, category_manager
    ) -> List[Category]:
        """Return all categories stored in Supabase
        with their corresponding things sorted from highest to lowest score."""
        try:
            categories_with_scores = {}
            categories = category_manager.get_categories()
            scores = self.get_all()
            for category in categories:
                categories_with_scores[category] = list(
                    filter(lambda score: score.category_name == category.name, scores)
                )
                categories_with_scores[category].sort(
                    key=lambda score: score.num_votes, reverse=True
                )
                categories_with_scores[category] = categories_with_scores[category][
                    :num_scores_per_category
                ]
            return categories_with_scores
        except httpx.HTTPError as e:
            raise ConnectionError(str(e)) from e

    def get_things_with_votes(self, user_id: str):
        try:
            response = (
                self.supabase.from_("v_things_with_votes")
                .select("*")
                .eq("user_id", user_id)
                .execute()
            )

            things_with_votes: Dict[str, List[Dict[str:str]]] = {}
            for row in response.data:
                if row["thing_name"] not in things_with_votes:
                    things_with_votes[row["thing_name"]] = []
                things_with_votes[row["thing_name"]].append(row)

            # sort by thing with most votes first
            things_with_votes = dict(
                sorted(things_with_votes.items(), key=lambda e: len(e[1]), reverse=True)
            )

            return things_with_votes
        except httpx.HTTPError as e:
            raise ConnectionError(str(e)) from e
