import uuid


class Thing:
    def __init__(self, name, from_thing_name=None, created_at=None, img_filename=None):
        if not from_thing_name:
            from_thing_name = None
        if not created_at:
            created_at = None
        if not img_filename:
            img_filename = None
        self.created_at = created_at
        self.name = name
        self.img_filename = img_filename
        self.from_thing_name = from_thing_name

    def __str__(self):
        return (
            f"Thing("
            f"name='{self.name}', "
            f"from_thing_name='{self.from_thing_name}', "
            f"created_at='{self.created_at}', "
            f"img_filename='{self.img_filename}'"
            f")"
        )

    def from_json(json):
        thing = Thing(
            created_at=json["created_at"],
            name=json["name"],
            from_thing_name=json["from_thing_name"],
            img_filename=json["img_filename"],
        )
        return thing

    def from_request(request, img_filename=None):
        if not request.form.get("thingName"):
            raise ValueError()

        return Thing(
            name=request.form.get("thingName"),
            from_thing_name=request.form.get("fromThingName"),
            img_filename=img_filename,
        )
