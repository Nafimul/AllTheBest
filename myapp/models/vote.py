from typing import Any, Dict, Optional


class Vote:
    def __init__(
        self,
        user_id: str,
        thing_name: str,
        category_name: str,
        spoiler_for: Optional[str] = None,
        comment: Optional[str] = None,
        created_at: Optional[str] = None,
        is_favorite: bool = False,
    ) -> None:
        if not isinstance(user_id, str):
            raise TypeError("user_id must be a string")
        if not user_id.strip():
            raise ValueError("user_id is required")

        if not isinstance(thing_name, str):
            raise TypeError("thingName must be a string")
        if not thing_name.strip():
            raise ValueError("thingName is required")

        if not isinstance(category_name, str):
            raise TypeError("categoryName must be a string")
        if not category_name.strip():
            raise ValueError("categoryName is required")

        self.user_id = user_id.strip()
        self.thing_name = thing_name.strip()
        self.category_name = category_name.strip()
        self.spoiler_for = spoiler_for
        self.comment = comment
        self.created_at = created_at
        self.is_favorite = is_favorite

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "Vote":
        return cls(
            created_at=data.get("created_at"),
            user_id=str(data.get("user_id")),
            thing_name=str(data.get("thing_name")),
            category_name=str(data.get("category_name")),
            spoiler_for=data.get("spoiler_for"),
            comment=data.get("comment"),
            is_favorite=bool(data.get("is_favorite", False)),
        )

    def to_json(self) -> Dict[str, Any]:
        return {
            "created_at": self.created_at,
            "user_id": self.user_id,
            "thing_name": self.thing_name,
            "category_name": self.category_name,
            "spoiler_for": self.spoiler_for,
            "comment": self.comment,
            "is_favorite": self.is_favorite,
        }

    @classmethod
    def from_request(cls, request: Any, user_id: str) -> "Vote":
        if not isinstance(user_id, str):
            raise TypeError("user_id must be a string")
        if not user_id.strip():
            raise ValueError("user_id is required")

        return cls(
            category_name=request.form.get("categoryName"),
            user_id=user_id.strip(),
            thing_name=request.form.get("thingName"),
            spoiler_for=request.form.get("voteSpoilerFor"),
            comment=request.form.get("voteComment"),
            is_favorite=bool(request.form.get("voteIsFavorite")),
        )
