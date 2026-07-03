from typing import Any, List, Optional
import httpx

from myapp.models.category import Category
from myapp.models.score import Score


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

    def get_categories_with_scores(self, scores_per_category) -> List[Category]:
        """Return all categories stored in Supabase
        with their corresponding things sorted from highest to lowest score."""
        try:
            categories_with_scores = {}
            categories = self.get_categories()
            scores = self.get_scores()
            for category in categories:
                categories_with_scores[category] = list(
                    filter(lambda score: score.category_name == category.name, scores)
                )
                categories_with_scores[category].sort(
                    key=lambda score: score.num_votes, reverse=True
                )
                categories_with_scores[category] = categories_with_scores[category][
                    :scores_per_category
                ]
            return categories_with_scores
        except httpx.HTTPError as e:
            raise ConnectionError(str(e)) from e
