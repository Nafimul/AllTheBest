from typing import Any, List, Optional

import httpx

from myapp.models.score import Score
from myapp.models.vote import Vote


class SupabaseVoteManager:
    def __init__(self, get_supabase_client_fn: Any) -> None:
        self.get_supabase = get_supabase_client_fn

    def get_all(self) -> List[Vote]:
        """Return all votes stored in Supabase."""
        try:
            response = self.get_supabase().table("votes").select("*").execute()
            items = []
            for item in response.data:
                items.append(Vote.from_json(item))
            return items
        except httpx.HTTPError as e:
            raise ConnectionError(str(e)) from e

    def get_by_user_id(self, user_id) -> List[Vote]:
        try:
            response = (
                self.get_supabase()
                .table("votes")
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

    def get_vote(
        self, user_id: str, category_name: str, thing_name: str
    ) -> Optional[Vote]:
        """Return a specific vote by user_id, category_name, and thing_name."""
        try:
            response = (
                self.get_supabase()
                .table("votes")
                .select("*")
                .filter("user_id", "eq", user_id)
                .filter("category_name", "eq", category_name)
                .filter("thing_name", "eq", thing_name)
                .execute()
            )
            if response.data:
                return Vote.from_json(response.data[0])
            return None
        except httpx.HTTPError as e:
            raise ConnectionError(str(e)) from e

    def upsert(self, vote: Vote, spoiler_for: Optional[str]) -> Vote:
        """Insert or update a vote record."""
        if not isinstance(vote, Vote):
            raise TypeError("vote must be a Vote instance")
        if spoiler_for and not isinstance(spoiler_for, str):
            raise TypeError("spoiler_for must be a str instance")

        try:
            row_json = vote.to_json()
            row_json.pop("created_at", None)
            response = self.get_supabase().table("votes").upsert(row_json).execute()
            if not response.data:
                raise ConnectionError("Vote upsert did not return data")
            response = (
                self.get_supabase()
                .table("scores")
                .update({"spoiler_for": spoiler_for})
                .eq("category_name", vote.category_name)
                .eq("thing_name", vote.thing_name)
                .execute()
            )
            if not response.data:
                raise ConnectionError()
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
                self.get_supabase()
                .table("votes")
                .delete()
                .filter("category_name", "eq", vote.category_name)
                .filter("user_id", "eq", vote.user_id)
                .execute()
            )
            if not response.data:
                raise ConnectionError("Vote upsert did not return data")
        except httpx.HTTPError as e:
            raise ConnectionError(str(e)) from e
