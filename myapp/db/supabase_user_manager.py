from typing import Any, Optional

import httpx
from supabase import AuthError

from myapp.errors.authentication_error import AuthenticationError
from myapp.models.user import User


class SupabaseUserManager:
    def __init__(self, supabase: Any) -> None:
        """Manage Supabase authentication operations."""
        self.supabase = supabase

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
        """Return the currently authenticated user, or None if not available."""
        try:
            response = self.supabase.auth.get_user()
            if response is None or response.user is None:
                return None

            data = response.model_dump()
            return User.from_supabase_row_json(data["user"])
        except httpx.HTTPError as e:
            raise ConnectionError(str(e)) from e
