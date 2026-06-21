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
            name=json["name"],
            created_at=json["created_at"],
            is_spoiler=json["is_spoiler"],
            desc=json["desc"],
            is_negative=json["is_negative"],
        )
        return category

    def from_request(request):
        if not request.form.get("categoryName"):
            raise ValueError()

        return Category(
            name=request.form.get("categoryName"),
            is_spoiler=True if request.form.get("categoryIsSpoiler") else False,
            desc=request.form.get("categoryDesc"),
            is_negative=True if request.form.get("categoryIsNegative") else False,
        )
