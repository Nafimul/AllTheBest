class Thing:
    def __init__(self, name, from_thing_id=None, image_url=None, id=None, created_at=None):
        self.id = id
        self.created_at = created_at
        self.name = name
        self.from_thing_id = from_thing_id
        self.image_url = image_url