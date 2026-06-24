import io
from pathlib import Path
from typing import Any, Optional

import httpx
from PIL import Image
from werkzeug.datastructures import FileStorage

from myapp.models.thing import Thing


class SupabaseThingManager:
    def __init__(self, supabase: Any) -> None:
        """Create a thing manager for Supabase operations."""
        self.supabase = supabase

    def get_thing(self, name: str) -> Optional[Thing]:
        """Return a Thing by name or None if not found."""
        if not isinstance(name, str):
            raise TypeError("name must be a string")
        if not name.strip():
            raise ValueError("name is required and must be a non-empty string")

        try:
            response = (
                self.supabase.table("things")
                .select("*")
                .filter("name", "eq", name.strip())
                .execute()
            )
            if not response.data:
                return None
            return Thing.from_json(response.data[0])
        except httpx.HTTPError as e:
            raise ConnectionError(str(e)) from e

    def upsert_thing(
        self, thing: Thing, img_file: Optional[FileStorage] = None
    ) -> Thing:
        """Insert or update a Thing and its optional image."""
        if thing is None:
            raise ValueError("thing is required")
        if not isinstance(thing, Thing):
            raise TypeError("thing must be a Thing instance")

        if img_file is not None and img_file.filename:
            img_file.filename = thing.name + ".JPEG"
            self.upsert_image(img_file)
            thing.img_path = self.get_img_path(thing.name)

        try:
            row_json = thing.to_json()
            row_json.pop("created_at", None)
            response = self.supabase.table("things").upsert(row_json).execute()
            return Thing.from_json(response.data[0])
        except httpx.HTTPError as e:
            raise ConnectionError(str(e)) from e

    def _prepare_image_bytes(self, img_file: FileStorage) -> bytes:
        """
        Resize the uploaded image while preserving aspect ratio.
        Also converts img_file to JPEG and renames file extenstion to JPEG.
        """
        if img_file is None:
            raise ValueError("img_file is required")
        if not isinstance(img_file, FileStorage):
            raise TypeError("img_file must be FileStorage")
        if not img_file.filename:
            raise ValueError("Image filename is required")
        if not getattr(img_file, "mimetype", "").startswith("image/"):
            raise ValueError("Uploaded file must be an image")

        try:
            img_file.stream.seek(0)
        except Exception as e:
            raise ValueError("Invalid uploaded image stream") from e

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

            file_name_without_ext = Path(img_file.filename).stem
            img_file.filename = file_name_without_ext + ".JPEG"
            return buffer.getvalue()

    def upsert_image(self, img_file: FileStorage) -> None:
        """Upload a validated and resized image to Supabase storage."""
        image_bytes = self._prepare_image_bytes(img_file)
        try:
            self.supabase.storage.from_("ThingImages").upload(
                file=image_bytes,
                path=img_file.filename,
                file_options={
                    "upsert": "true",
                    "content-type": "image/jpeg",
                },
            )
        except httpx.HTTPError as e:
            raise ConnectionError(str(e)) from e

    def get_img_path(self, img_filename: str) -> str:
        """Return a public image URL for a stored thing image."""
        if not isinstance(img_filename, str):
            raise TypeError("img_filename must be a string")
        if not img_filename.strip():
            raise ValueError("img_filename is required")

        try:
            image_url = self.supabase.storage.from_("ThingImages").get_public_url(
                img_filename.strip()
            )
            return image_url
        except httpx.HTTPError as e:
            raise ConnectionError(str(e)) from e
