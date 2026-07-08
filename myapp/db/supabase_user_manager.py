from typing import Any, List, Optional

import httpx
from supabase import AuthError
from flask import request

from myapp.errors.authentication_error import AuthenticationError
from myapp.models.profile import Profile
from myapp.models.user import User


class SupabaseUserManager:
    def __init__(self, get_supabase_client_fn: Any) -> None:
        """Manage Supabase authentication operations."""
        self.get_supabase = get_supabase_client_fn

    @property
    def supabase(self) -> Any:
        """Dynamically get the isolated Supabase client for the current request."""
        return self.get_supabase()

    def signup(self, email: str, password: str, name: str) -> User:
        """Register a new user with email, password, and name."""
        if not isinstance(email, str):
            raise TypeError("email must be a string")
        if not email:
            raise ValueError("email is required")
        if not isinstance(password, str):
            raise TypeError("password must be a string")
        if not password:
            raise ValueError("password is required")
        if not isinstance(name, str):
            raise TypeError("name must be a string")
        if not name:
            raise ValueError("name is required")

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
            raise AuthenticationError("email or name already in use") from e
        except httpx.HTTPError as e:
            raise ConnectionError(str(e)) from e

    def login(self, email: str, password: str) -> User:
        """Authenticate a user by email and password."""
        if not isinstance(email, str):
            raise TypeError("email must be a string")
        if not email:
            raise ValueError("email is required")
        if not isinstance(password, str):
            raise TypeError("password must be a string")
        if not password:
            raise ValueError("password is required")

        try:
            response = self.supabase.auth.sign_in_with_password(
                {"email": email, "password": password}
            )
            data = response.model_dump()
            return User.from_supabase_row_json(data["user"])
        except AuthError as e:
            raise AuthenticationError("Invalid email or password") from e
        except httpx.HTTPError as e:
            raise ConnectionError(str(e)) from e

    def get_user(self) -> Optional[User]:
        """Return the currently authenticated user using incoming browser cookies."""
        try:
            access_token = request.cookies.get("sb-access-token")
            refresh_token = request.cookies.get("sb-refresh-token")

            if not access_token or not refresh_token:
                return None

            # Seed this request's specific isolated client with the user's personal tokens
            self.supabase.auth.set_session(access_token, refresh_token)

            response = self.supabase.auth.get_user()
            if response is None or response.user is None:
                return None

            data = response.model_dump()
            return User.from_supabase_row_json(data["user"])
        except Exception:
            return None

    def get_profile_by_id(self, user_id: str) -> Optional[User]:
        """Return a profile by their ID, or None if not found."""
        if not isinstance(user_id, str):
            raise TypeError("user_id must be a string")

        try:
            response = (
                self.supabase.table("profiles")
                .select("*")
                .filter("user_id", "eq", user_id)
                .execute()
            )
            if response is None:
                return None
            return Profile.from_json(response.data[0])
        except httpx.HTTPError as e:
            raise ConnectionError(str(e)) from e

    def get_profiles(self) -> List[Profile]:
        """Return all things stored in Supabase."""
        try:
            response = self.supabase.table("profiles").select("*").execute()
            items = []
            for item in response.data:
                items.append(Profile.from_json(item))
            return items
        except httpx.HTTPError as e:
            raise ConnectionError(str(e)) from e
