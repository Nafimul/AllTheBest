from typing import Any, Dict

import flask_login


class User(flask_login.UserMixin):
    def __init__(self, id, name, email=None):
        if (
            (not isinstance(id, str))
            or not isinstance(name, str)
            or (email and not isinstance(email))
        ):
            raise TypeError()

        self.id = id
        self.name = name
        self.email = email

    @classmethod
    def from_supabase_row_json(cls, data: Dict[str, Any]) -> "User":
        id = data.get("id")
        email = data.get("email")
        metadata = data.get("user_metadata")

        if not isinstance(metadata, dict) or not isinstance(metadata.get("name"), str):
            raise TypeError()

        return cls(id, metadata.get("name"), email)
