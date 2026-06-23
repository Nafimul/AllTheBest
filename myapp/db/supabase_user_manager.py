import httpx
from postgrest import APIError
import storage3
from supabase import AuthError, create_client, Client
import supabase_auth
from myapp.errors.authentication_error import AuthenticationError
from myapp.models.category import Category
from myapp.models.thing import Thing
from myapp.models.user import User


class SupabaseUserManager:
    def __init__(self, supabase):
        self.supabase = supabase

    def signup(self, email, password, name):
        try:
            response = self.supabase.auth.sign_up(
                {
                    "email": email,
                    "password": password,
                    "options": {"data": {"name": name}},
                }
            )

            data = response.model_dump()
            return User.from_supabase_row_json(data["user"])
        except AuthError as e:
            raise AuthenticationError("email or name already in use", e.code)
        except httpx.HTTPError as e:
            raise ConnectionError(e.args)

    def login(self, email, password):
        try:
            response = self.supabase.auth.sign_in_with_password(
                {"email": email, "password": password}
            )

            data = response.model_dump()
            return User.from_supabase_row_json(data["user"])
        except AuthError as e:
            raise AuthenticationError("Invalid email or password", e.code)
        except httpx.HTTPError as e:
            raise ConnectionError(e.args)

    def get_user(self):
        try:
            response = self.supabase.auth.get_user()
            if response is None or response.user is None:
                return None

            data = response.model_dump()
            return User.from_supabase_row_json(data["user"])
        except httpx.HTTPError as e:
            raise ConnectionError(e.args)
