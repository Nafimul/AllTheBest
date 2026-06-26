from typing import Any, Dict, Optional


class Thing:
    def __init__(
        self,
        name: str,
        from_thing_name: Optional[str] = None,
        created_at: Optional[str] = None,
        img_path: Optional[str] = None,
    ) -> None:
        if (
            (from_thing_name and not isinstance(from_thing_name, str))
            or (not isinstance(name, str))
            or (created_at and not isinstance(created_at, str))
            or (img_path and not isinstance(img_path, str))
        ):
            raise TypeError()
        if not name.strip():
            raise ValueError("thingName is required and must be a non-empty string")

        self.created_at = created_at
        self.name = name.strip()
        self.img_path = img_path
        self.from_thing_name = from_thing_name

    def __str__(self):
        return (
            f"Thing("
            f"name='{self.name}', "
            f"from_thing_name='{self.from_thing_name}', "
            f"created_at='{self.created_at}', "
            f"img_path='{self.img_path}'"
            f")"
        )

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "Thing":
        name = data.get("name")
        from_thing_name = data.get("from_thing_name")
        img_path = data.get("img_path")
        created_at = data.get("created_at")

        return cls(
            name=name,
            from_thing_name=from_thing_name,
            created_at=created_at,
            img_path=img_path,
        )

    def to_json(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "from_thing_name": self.from_thing_name,
            "created_at": self.created_at,
            "img_path": self.img_path,
        }

    @classmethod
    def from_request(cls, request: Any) -> "Thing":
        thing_name = request.form.get("thingName")
        if not isinstance(thing_name, str):
            raise TypeError("thingName must be a string")
        if not thing_name.strip():
            raise ValueError("thingName is required")

        from_thing_name = request.form.get("fromThingName")
        if isinstance(from_thing_name, str) and not from_thing_name.strip():
            from_thing_name = None

        return cls(name=thing_name.strip(), from_thing_name=from_thing_name)
