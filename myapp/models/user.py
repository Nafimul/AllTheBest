from typing import Any, Dict

import flask_login


class User(flask_login.UserMixin):
    @classmethod
    def from_supabase_row_json(cls, data: Dict[str, Any]) -> "User":
        user_id = data.get("id")
        email = data.get("email")
        metadata = data.get("user_metadata")
        name = None
        if isinstance(metadata, dict):
            name = metadata.get("name")

        if not isinstance(user_id, str):
            raise TypeError("User id in auth response must be a string")
        if not user_id.strip():
            raise ValueError("User id is missing in auth response")
        if not isinstance(name, str):
            raise TypeError("User name in auth response must be a string")
        if not name.strip():
            raise ValueError("User name is missing in auth response")

        user = cls()
        user.id = user_id.strip()
        if isinstance(email, str):
            user.email = email.strip()
        user.name = name.strip()
        return user
