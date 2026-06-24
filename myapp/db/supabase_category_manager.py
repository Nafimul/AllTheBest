from typing import Any, List

import httpx

from myapp.models.category import Category


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
