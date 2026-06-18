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
from myapp.user import User


class SupabaseUserManager:
    def __init__(self, url, key):
        self.supabase = create_client(url, key)

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
        except APIError as e:
            raise ServerError("server error", e.code)

    def login(self, email, password):
        try:
            response = self.supabase.auth.sign_in_with_password(
                {"email": email, "password": password}
            )

            data = response.model_dump()
            return User.from_supabase_row_json(data["user"])
        except AuthError as e:
            raise AuthenticationError("Invalid email or password", e.code)
        except APIError as e:
            raise ServerError("server error", e.code)

    def get_user(self):
        try:
            response = self.supabase.auth.get_user()
            if response is None or response.user is None:
                return None

            data = response.model_dump()
            return User.from_supabase_row_json(data["user"])
        except APIError as e:
            raise ServerError("server error", e.code)
