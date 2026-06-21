from postgrest import APIError
import storage3
from supabase import AuthError, create_client, Client
import supabase_auth
from myapp.errors.authentication_error import AuthenticationError
from myapp.errors.db_state_error import DbStateError
from myapp.errors.error_categorizer import is_client_error
from myapp.errors.server_error import ServerError
from myapp.models.category import Category
from myapp.models.thing import Thing
from myapp.models.user import User


class SupabaseCategoryManager:
    def __init__(self, supabase):
        self.supabase = supabase

    def get_categories(self):
        try:
            response = self.supabase.table("categories").select("*").execute()
        except APIError as e:
            raise ServerError("server error", e.code)
        categories = []
        for item in response.data:
            categories.append(Category.from_json(item))
        return categories

    def upsert(self, category):
        try:
            row_json = category.to_json()
            row_json.pop("created_at")
            response = self.supabase.table("categories").upsert(row_json).execute()

            return Category.from_json(response.data[0])
        except APIError as e:
            if is_client_error(e.code):
                raise DbStateError("That category already exists", e.code)
            raise ServerError("server error", e.code)
