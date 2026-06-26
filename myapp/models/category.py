from typing import Any, Dict, List, Optional


class Category:
    def __init__(
        self,
        name: str,
        created_at: Optional[str] = None,
        is_spoiler: bool = False,
        desc: Optional[str] = None,
        is_negative: bool = False,
    ) -> None:
        if not isinstance(name, str):
            raise TypeError("categoryName must be a string")
        if not name.strip():
            raise ValueError("categoryName is required and must be a non-empty string")
        if (
            (created_at and not isinstance(created_at, str))
            or (not isinstance(is_spoiler, bool))
            or (desc and not isinstance(desc, str))
            or (not isinstance(is_negative, bool))
        ):
            raise TypeError()

        self.created_at = created_at
        self.name = name.strip()
        self.is_spoiler = is_spoiler
        self.desc = desc
        self.is_negative = is_negative

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "Category":
        return cls(
            name=data.get("name"),
            created_at=data.get("created_at"),
            is_spoiler=bool(data.get("is_spoiler", False)),
            desc=data.get("desc"),
            is_negative=bool(data.get("is_negative", False)),
        )

    def to_json(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "created_at": self.created_at,
            "is_spoiler": self.is_spoiler,
            "desc": self.desc,
            "is_negative": self.is_negative,
        }

    @classmethod
    def from_request(cls, request: Any) -> "Category":
        category_name = request.form.get("categoryName")
        if not isinstance(category_name, str):
            raise TypeError("categoryName must be a string")
        if not category_name.strip():
            raise ValueError("categoryName is required")

        return cls(
            name=category_name.strip(),
            is_spoiler=bool(request.form.get("categoryIsSpoiler")),
            desc=request.form.get("categoryDesc"),
            is_negative=bool(request.form.get("categoryIsNegative")),
        )
