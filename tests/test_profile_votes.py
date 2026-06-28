import unittest

from myapp import build_profile_vote_entries
from myapp.models.thing import Thing
from myapp.models.vote import Vote


class DummyThingManager:
    def get_thing(self, name: str):
        if name == "Coffee":
            return Thing(name=name, img_path="/images/coffee.jpg")
        return None


class ProfileVoteEntriesTests(unittest.TestCase):
    def test_favorites_are_sorted_first_and_include_thing_data(self) -> None:
        votes = [
            Vote(user_id="user-1", thing_name="Tea", category_name="Drinks"),
            Vote(
                user_id="user-1",
                thing_name="Coffee",
                category_name="Drinks",
                is_favorite=True,
            ),
        ]

        entries = build_profile_vote_entries(votes, DummyThingManager())

        self.assertEqual(entries[0]["vote"].thing_name, "Coffee")
        self.assertTrue(entries[0]["vote"].is_favorite)
        self.assertEqual(entries[0]["thing"].img_path, "/images/coffee.jpg")
        self.assertEqual(entries[1]["vote"].thing_name, "Tea")


if __name__ == "__main__":
    unittest.main()
