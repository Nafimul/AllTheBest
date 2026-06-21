from postgrest import APIError
import storage3
from supabase import AuthError, create_client, Client
import supabase_auth
from myapp.errors.authentication_error import AuthenticationError
from myapp.errors.db_state_error import DbStateError
from myapp.errors.server_error import ServerError
from myapp.models.category import Category
from myapp.models.thing import Thing
from myapp.models.user import User


class SupabaseThingManager:
    def __init__(self, supabase):
        self.supabase = supabase

    def get_thing(self, name: str):
        try:
            response = (
                self.supabase.table("things")
                .select("*")
                .filter("name", "eq", name)
                .execute()
            )
            if len(response.data) == 0:
                return None
            return Thing.from_json(response.data[0])
        except APIError as e:
            raise ServerError("server error", e.code)

    # def update_thing(self, thing: Thing):
    #     try:
    #         if self.get_thing_by_id(thing.from_thing_id) is None:
    #             raise DbStateError("from thing not found", 404)
    #         if self.get_thing(thing.name) is None:
    #             raise DbStateError("thing with that name not found", 404)
    #         if thing.from_thing_name is not None and self.get_thing(thing.from_thing_name) is None:
    #             raise DbStateError("from thing not found", 404)

    #         response = self.supabase.table('things').update({
    #             "image_url": thing.image_url,
    #             "from_thing_name": thing.from_thing_name
    #             }).eq("name", thing.name).execute()

    #         return Thing.from_json(response.data[0])
    #     except APIError as e:
    #         raise ServerError("server error", e.code)

    # def add_thing(self, thing: Thing):
    #     try:
    #         if self.get_thing(thing.name) is not None:
    #             raise DbStateError("That thing already exists")
    #         if thing.from_thing_name is not None and self.get_thing(thing.from_thing_name) is None:
    #             raise DbStateError("from thing not found", 404)

    #         response = self.supabase.table('things').insert({
    #             "name": thing.name,
    #             "image_url": thing.image_url,
    #             "from_thing_id": thing.from_thing_id
    #             }).execute()

    #         return Thing.from_json(response.data[0])
    #     except APIError as e:
    #         raise ServerError("server error", e.code)

    def upsert_thing(self, thing: Thing, img_file=None):
        try:
            if (
                thing.from_thing_name is not None
                and self.get_thing(thing.from_thing_name) is None
            ):
                raise DbStateError("from thing not found", 404)

            if img_file:
                img_file.filename = thing.name
                self.upsert_image(img_file)
                thing.img_path = self.get_img_path(thing.name)

            row_json = thing.to_json()
            row_json.pop("created_at")
            response = self.supabase.table("things").upsert(row_json).execute()

            return Thing.from_json(response.data[0])
        except APIError as e:
            print(e.message)
            raise ServerError("server error", e.code)

    def upsert_image(self, img_file):
        try:
            self.supabase.storage.from_("ThingImages").upload(
                file=img_file.read(),
                path=img_file.filename,
                file_options={
                    "upsert": "true",
                    "content-type": img_file.content_type,
                },
            )
        except (APIError, storage3.exceptions.StorageApiError) as e:
            raise ServerError("server error", e.code)

    def get_img_path(self, img_filename):
        try:
            image_url = self.supabase.storage.from_("ThingImages").get_public_url(
                img_filename
            )
            return image_url
        except (APIError, storage3.exceptions.StorageApiError) as e:
            raise ServerError("server error", e.code)
