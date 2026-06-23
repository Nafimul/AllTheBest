import io

import httpx
from PIL import Image
from postgrest import APIError
import storage3
from supabase import AuthError, create_client, Client
import supabase_auth
from werkzeug.datastructures import FileStorage
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
        except httpx.HTTPError as e:
            raise ConnectionError(e.message)

    def upsert_thing(self, thing: Thing, img_file=None):
        try:
            if (
                thing.from_thing_name is not None
                and self.get_thing(thing.from_thing_name) is None
            ):
                raise ValueError("from thing does not exist", 404)

            if img_file:
                img_file.filename = thing.name
                self.upsert_image(img_file)
                thing.img_path = self.get_img_path(thing.name)

            row_json = thing.to_json()
            row_json.pop("created_at")
            response = self.supabase.table("things").upsert(row_json).execute()

            return Thing.from_json(response.data[0])
        except httpx.HTTPError as e:
            raise ConnectionError(e.message)

    def _prepare_image_bytes(self, img_file: FileStorage) -> bytes:
        """Resize and encode a FileStorage image as optimized JPEG bytes."""
        img_file.stream.seek(0)

        with Image.open(img_file.stream) as img:
            max_width, max_height = 1024, 1024
            width, height = img.size
            if width > max_width or height > max_height:
                scale = min(max_width / width, max_height / height)
                new_width = int(width * scale)
                new_height = int(height * scale)
                img = img.resize((new_width, new_height), Image.LANCZOS)

            if img.mode not in ("RGB", "L"):
                img = img.convert("RGB")

            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=80, optimize=True)
            return buffer.getvalue()

    def upsert_image(self, img_file: FileStorage):
        try:
            image_bytes = self._prepare_image_bytes(img_file)
            self.supabase.storage.from_("ThingImages").upload(
                file=image_bytes,
                path=img_file.filename,
                file_options={
                    "upsert": "true",
                    "content-type": "image/jpeg",
                },
            )
        except httpx.HTTPError as e:
            raise ConnectionError(e.message)

    def get_img_path(self, img_filename):
        try:
            image_url = self.supabase.storage.from_("ThingImages").get_public_url(
                img_filename
            )
            return image_url
        except httpx.HTTPError as e:
            raise ConnectionError(e.message)
