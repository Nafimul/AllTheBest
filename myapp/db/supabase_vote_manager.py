from typing import Any, List

import httpx

from myapp.models.vote import Vote


class SupabaseVoteManager:
    def __init__(self, supabase: Any) -> None:
        """Manage vote CRUD operations in Supabase."""
        self.supabase = supabase

    def get_all(self) -> List[Vote]:
        """Return all votes stored in Supabase."""
        try:
            response = self.supabase.table("votes").select("*").execute()
            items = []
            for item in response.data:
                items.append(Vote.from_json(item))
            return items
        except httpx.HTTPError as e:
            raise ConnectionError(str(e)) from e

    def get_by_user_id(self, user_id) -> List[Vote]:
        """Return all votes stored in Supabase."""
        try:
            response = (
                self.supabase.table("votes")
                .select("*")
                .filter("user_id", "eq", user_id)
                .execute()
            )
            items = []
            for item in response.data:
                items.append(Vote.from_json(item))
            return items
        except httpx.HTTPError as e:
            raise ConnectionError(str(e)) from e

    def upsert(self, vote: Vote) -> Vote:
        """Insert or update a vote record."""
        if vote is None:
            raise ValueError("vote is required")
        if not isinstance(vote, Vote):
            raise TypeError("vote must be a Vote instance")

        try:
            row_json = vote.to_json()
            row_json.pop("created_at", None)
            response = self.supabase.table("votes").upsert(row_json).execute()
            if not response.data:
                raise ConnectionError("Vote upsert did not return data")
            return Vote.from_json(response.data[0])
        except httpx.HTTPError as e:
            raise ConnectionError(str(e)) from e

    def delete(self, vote: Vote) -> Vote:
        """Insert or update a vote record."""
        if vote is None:
            raise ValueError("vote is required")
        if not isinstance(vote, Vote):
            raise TypeError("vote must be a Vote instance")

        try:
            response = (
                self.supabase.table("votes")
                .delete()
                .filter("category_name", "eq", vote.category_name)
                .filter("user_id", "eq", vote.user_id)
                .execute()
            )
            if not response.data:
                raise ConnectionError("Vote upsert did not return data")
        except httpx.HTTPError as e:
            raise ConnectionError(str(e)) from e
