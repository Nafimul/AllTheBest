import httpx
from postgrest import APIError
import storage3
from supabase import AuthError, create_client, Client
import supabase_auth
from myapp.models.category import Category
from myapp.models.thing import Thing
from myapp.models.user import User


class SupabaseCategoryManager:
    def __init__(self, supabase):
        self.supabase = supabase

    def get_categories(self):
        try:
            response = self.supabase.table("categories").select("*").execute()
            categories = []
            for item in response.data:
                categories.append(Category.from_json(item))
            return categories
        except httpx.HTTPError as e:
            raise ConnectionError(e.message)

    def upsert(self, category):
        try:
            row_json = category.to_json()
            row_json.pop("created_at")
            response = self.supabase.table("categafdsories").upsert(row_json).execute()

            return Category.from_json(response.data[0])
        except httpx.HTTPError as e:
            raise ConnectionError(e.message)
