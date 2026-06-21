class Vote:
    def __init__(
        self,
        user_id,
        thing_name,
        category_name,
        spoiler_for=None,
        comment=None,
        created_at=None,
        is_favorite=False,
    ):
        if not thing_name or not category_name or not user_id:
            raise ValueError()
        # if empty string, set to none instead.
        # because empty strings might override default values or mess up foreign key relationships if used in a db
        if not created_at:
            created_at = None

        self.user_id = user_id
        self.thing_name = thing_name
        self.category_name = category_name
        self.spoiler_for = spoiler_for
        self.comment = comment
        self.created_at = created_at
        self.is_favorite = is_favorite

    def from_json(json):
        return Vote(
            created_at=json.get("created_at"),
            user_id=json["user_id"],
            thing_name=json["thing_name"],
            category_name=json["category_name"],
            spoiler_for=json.get("spoiler_for"),
            comment=json.get("comment"),
            is_favorite=json.get("is_favorite", False),
        )

    def to_json(self):
        return {
            "created_at": self.created_at,
            "user_id": self.user_id,
            "thing_name": self.thing_name,
            "category_name": self.category_name,
            "spoiler_for": self.spoiler_for,
            "comment": self.comment,
            "is_favorite": self.is_favorite,
        }

    def from_request(request, user_id):
        return Vote(
            category_name=request.form.get("categoryName"),
            user_id=user_id,
            thing_name=request.form.get("thingName"),
            spoiler_for=request.form.get("voteSpoilerFor"),
            comment=request.form.get("voteComment"),
            is_favorite=True if request.form.get("voteIsFavorite") else False,
        )
