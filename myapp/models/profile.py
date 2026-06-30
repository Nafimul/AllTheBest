from typing import Any, Dict, List, Optional


class Profile:
    def __init__(
        self,
        user_id: str,
        name: str,
    ) -> None:
        if (not isinstance(user_id, str)) or (not isinstance(name, str)):
            raise TypeError()

        self.user_id = user_id
        self.name = name

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "Profile":
        return cls(
            user_id=data.get("user_id"),
            name=data.get("name"),
        )

    def to_json(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "user_id": self.user_id,
        }
