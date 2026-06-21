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

    def upsert_thing(self, thing: Thing):
        try:
            if (
                thing.from_thing_name is not None
                and self.get_thing(thing.from_thing_name) is None
            ):
                raise DbStateError("from thing not found", 404)

            response = (
                self.supabase.table("things")
                .upsert(
                    {
                        "name": thing.name,
                        "img_filename": thing.img_filename,
                        "from_thing_name": thing.from_thing_name,
                    }
                )
                .execute()
            )
            
            return Thing.from_json(response.data[0])
        except APIError as e:
            raise ServerError("server error", e.code)

    def add_image(self, img_file):
        try:
            self.supabase.storage.from_("ThingImages").upload(
                f"{img_file.filename}",
                img_file.read(),
                {"content-type": img_file.content_type},
            )
        except (APIError, storage3.exceptions.StorageApiError) as e:
            raise ServerError("server error", e.code)

    # def get_img_url(self, img_filename):
    #     try:
    #         image_url = self.supabase.storage.from_('ThingImages').get_public_url(f"{img_filename}")
    #         return image_url
    #     except (APIError, storage3.exceptions.StorageApiError) as e:
    #         raise ServerError("server error", e.code)

    def signup(self, email, password, name):
        try:
            response = self.supabase.auth.sign_up(
                {
                    "email": email,
                    "password": password,
                    "options": {"data": {"name": name}},
                }
            )

            data = response.model_dump()
            return User.from_supabase_row_json(data["user"])
        except AuthError as e:
            raise AuthenticationError("email or name already in use", e.code)
        except APIError as e:
            raise ServerError("server error", e.code)
