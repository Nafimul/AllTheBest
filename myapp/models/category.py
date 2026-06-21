class Category:
    def __init__(
        self, name, created_at=None, is_spoiler=False, desc=None, is_negative=False
    ):
        self.created_at = created_at
        self.name = name
        self.is_spoiler = is_spoiler
        self.desc = desc
        self.is_negative = is_negative

    def from_json(json):
        category = Category(
            name=json.get("name"),
            created_at=json.get("created_at"),
            is_spoiler=json.get("is_spoiler"),
            desc=json.get("desc"),
            is_negative=json.get("is_negative", False),
        )
        return category

    def to_json(self):
        return {
            "name": self.name,
            "created_at": self.created_at,
            "is_spoiler": self.is_spoiler,
            "desc": self.desc,
            "is_negative": self.is_negative,
        }

    def from_request(request):
        if not request.form.get("categoryName"):
            raise ValueError()

        return Category(
            name=request.form.get("categoryName"),
            is_spoiler=True if request.form.get("categoryIsSpoiler") else False,
            desc=request.form.get("categoryDesc"),
            is_negative=True if request.form.get("categoryIsNegative") else False,
        )
