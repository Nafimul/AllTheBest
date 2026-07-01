from typing import Any, Dict, Optional


class Thing:
    def __init__(
        self,
        name: str,
        created_at: Optional[str] = None,
        img_path: Optional[str] = None,
    ) -> None:
        if (
            (not isinstance(name, str))
            or (created_at and not isinstance(created_at, str))
            or (img_path and not isinstance(img_path, str))
        ):
            raise TypeError()

        self.created_at = created_at
        self.name = name
        self.img_path = img_path

    def __str__(self):
        return (
            f"Thing("
            f"name='{self.name}', "
            f"created_at='{self.created_at}', "
            f"img_path='{self.img_path}'"
            f")"
        )

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "Thing":
        name = data.get("name")
        img_path = data.get("img_path")
        created_at = data.get("created_at")

        return cls(
            name=name,
            created_at=created_at,
            img_path=img_path,
        )

    def to_json(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "created_at": self.created_at,
            "img_path": self.img_path,
        }

    @classmethod
    def from_request(cls, request: Any) -> "Thing":
        thing_name = request.form.get("thingName")
        if not isinstance(thing_name, str):
            raise TypeError("thingName must be a string")
        if not thing_name:
            raise ValueError("thingName is required")

        return cls(name=thing_name)
