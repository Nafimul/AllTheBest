from typing import Any, List
import httpx

from myapp.models.category import Category
from myapp.models.score import Score


class SupabaseCategoryManager:
    def __init__(self, supabase: Any) -> None:
        """Manage category CRUD operations in Supabase."""
        self.supabase = supabase

    def get_categories(self) -> List[Category]:
        """Return all categories stored in Supabase."""
        try:
            response = self.supabase.table("categories").select("*").execute()
            categories = []
            for item in response.data:
                categories.append(Category.from_json(item))
            return categories
        except httpx.HTTPError as e:
            raise ConnectionError(str(e)) from e

    def upsert(self, category: Category) -> Category:
        """Insert or update a category record."""
        if category is None:
            raise ValueError("category is required")
        if not isinstance(category, Category):
            raise TypeError("category must be a Category instance")

        try:
            row_json = category.to_json()
            row_json.pop("created_at", None)
            response = self.supabase.table("categories").upsert(row_json).execute()
            if not response.data:
                raise ConnectionError("Category upsert did not return data")
            return Category.from_json(response.data[0])
        except httpx.HTTPError as e:
            raise ConnectionError(str(e)) from e

    def get_scores(self) -> List[Score]:
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
