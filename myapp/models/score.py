from typing import Any, Dict, Optional


class Score:
    def __init__(self, category_name: str, thing_name: str, num_votes: int) -> None:
        if (
            not isinstance(category_name, str)
            or not isinstance(thing_name, str)
            or not isinstance(num_votes, int)
        ):
            raise TypeError()

        self.category_name = category_name
        self.thing_name = thing_name
        self.num_votes = num_votes

    @classmethod
    def from_json(cls, data: Dict[str, Any]):
        return cls(
            category_name=data.get("category_name"),
            thing_name=data.get("thing_name"),
            num_votes=int(data.get("num_votes")),
        )

    def to_json(self) -> Dict[str, Any]:
        return {
            "category_name": self.category_name,
            "thing_name": self.thing_name,
            "num_votes": self.num_votes,
        }

    def __str__(self):
        return self.to_json()
