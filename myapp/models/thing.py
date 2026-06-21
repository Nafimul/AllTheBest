class Thing:
    def __init__(self, name, from_thing_name=None, created_at=None, img_path=None):
        self.created_at = created_at
        self.name = name
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

    def from_json(json):
        thing = Thing(
            created_at=json.get("created_at"),
            name=json.get("name"),
            from_thing_name=json.get("from_thing_name"),
            img_path=json.get("img_path"),
        )
        return thing

    def to_json(self):
        return {
            "name": self.name,
            "from_thing_name": self.from_thing_name,
            "created_at": self.created_at,
            "img_path": self.img_path,
        }

    def from_request(request):
        if not request.form.get("thingName"):
            raise ValueError()

        return Thing(
            name=request.form.get("thingName"),
            from_thing_name=(
                request.form.get("fromThingName")
                if request.form.get("fromThingName") is not ""
                else None
            ),
        )
