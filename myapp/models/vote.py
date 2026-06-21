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
            created_at=json["created_at"],
            user_id=json["user_id"],
            thing_name=json["thing_name"],
            category_name=json["category_name"],
            is_spoiler=json["is_spoiler"],
            comment=json["comment"],
            is_favorite=json["is_favorite"],
        )

    def from_request(request, user_id):
        return Vote(
            category_name=request.form.get("categoryName"),
            user_id=user_id,
            thing_name=request.form.get("thingName"),
            spoiler_for=request.form.get("voteSpoilerFor"),
            comment=request.form.get("voteComment"),
            is_favorite=request.form.get("voteIsFavorite"),
        )
