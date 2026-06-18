class Category:
    def __init__(
        self, name, created_at=None, is_spoiler=False, desc=None, is_negative=False
    ):
        self.created_at = created_at
        self.name = name
        self.is_spoiler = is_spoiler
        self.desc = desc

    def from_json(json):
        category = Category(
            name=json["name"],
            created_at=json["created_at"],
            is_spoiler=json["is_spoiler"],
            desc=json["desc"],
            is_negative=json["is_negative"],
        )
        return category
