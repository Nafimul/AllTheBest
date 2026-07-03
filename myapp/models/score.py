from typing import Any, Dict, Optional


class Score:
    def __init__(
        self,
        category_name: str,
        thing_name: str,
        num_votes: int,
        ranking: int,
        spoiler_for: Optional[str] = None,
    ) -> None:
        if (
            not isinstance(category_name, str)
            or (spoiler_for and not isinstance(spoiler_for, str))
            or not isinstance(thing_name, str)
            or not isinstance(num_votes, int)
            or not isinstance(ranking, int)
        ):
            raise TypeError()

        self.category_name = category_name
        self.spoiler_for = spoiler_for
        self.thing_name = thing_name
        self.num_votes = num_votes
        self.ranking = ranking

    @classmethod
    def from_json(cls, data: Dict[str, Any]):
        return cls(
            category_name=data.get("category_name"),
            thing_name=data.get("thing_name"),
            spoiler_for=data.get("spoiler_for"),
            num_votes=int(data.get("num_votes")),
            ranking=int(data.get("ranking")),
        )

    def to_json(self) -> Dict[str, Any]:
        return {
            "category_name": self.category_name,
            "thing_name": self.thing_name,
            "spoiler_for": self.spoiler_for,
            "num_votes": self.num_votes,
            "ranking": self.ranking,
        }

    def __str__(self):
        return self.to_json()
