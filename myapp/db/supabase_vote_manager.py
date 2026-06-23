import httpx
from postgrest import APIError
import storage3
from supabase import AuthError, create_client, Client
import supabase_auth
from myapp.models.category import Category
from myapp.models.thing import Thing
from myapp.models.user import User
from myapp.models.vote import Vote


class SupabaseVoteManager:
    def __init__(self, supabase):
        self.supabase = supabase

    def get_all(self):
        try:
            response = self.supabase.table("votes").select("*").execute()
            items = []
            for item in response.data:
                items.append(Vote.from_json(item))
            return items
        except httpx.HTTPError as e:
            raise ConnectionError()

    def upsert(self, vote):
        try:
            row_json = vote.to_json()
            row_json.pop("created_at")
            response = self.supabase.table("votes").upsert(row_json).execute()
            return Vote.from_json(response.data[0])
        except httpx.HTTPError as e:
            raise ConnectionError()
