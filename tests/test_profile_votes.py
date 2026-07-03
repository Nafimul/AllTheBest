import unittest

from myapp import build_current_user_votes, build_profile_vote_entries, build_score_row
from myapp.models.score import Score
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

    def test_spoiler_metadata_is_included_for_matching_votes(self) -> None:
        votes = [
            Vote(user_id="user-1", thing_name="Coffee", category_name="Drinks"),
        ]
        spoiler_for_by_thing = {("Coffee", "Drinks"): "The Matrix"}

        entries = build_profile_vote_entries(
            votes,
            DummyThingManager(),
            spoiler_for_by_thing=spoiler_for_by_thing,
        )

        self.assertEqual(entries[0]["spoiler_for"], "The Matrix")
        self.assertTrue(entries[0]["is_spoiler"])

    def test_spoiler_metadata_is_scoped_to_the_matching_category(self) -> None:
        votes = [
            Vote(user_id="user-1", thing_name="Coffee", category_name="Drinks"),
            Vote(user_id="user-1", thing_name="Coffee", category_name="Food"),
        ]
        spoiler_for_by_thing = {("Coffee", "Food"): "The Matrix"}

        entries = build_profile_vote_entries(
            votes,
            DummyThingManager(),
            spoiler_for_by_thing=spoiler_for_by_thing,
        )

        self.assertIsNone(entries[0]["spoiler_for"])
        self.assertFalse(entries[0]["is_spoiler"])
        self.assertEqual(entries[1]["spoiler_for"], "The Matrix")
        self.assertTrue(entries[1]["is_spoiler"])

    def test_score_row_includes_spoiler_metadata_for_matching_category(self) -> None:
        score = Score(
            category_name="Drinks",
            thing_name="Coffee",
            num_votes=5,
            spoiler_for="The Matrix",
        )
        row = build_score_row(
            score,
            [score],
            spoiler_for_by_thing={
                (score.thing_name, score.category_name): score.spoiler_for
            },
        )

        self.assertTrue(row["is_spoiler"])
        self.assertEqual(row["spoiler_for"], "The Matrix")

    def test_current_user_votes_are_collected_by_category(self) -> None:
        votes = [
            Vote(user_id="user-1", thing_name="Tea", category_name="Drinks"),
            Vote(
                user_id="user-1",
                thing_name="Coffee",
                category_name="Food",
                is_favorite=True,
            ),
        ]

        current_user_votes = build_current_user_votes(votes)

        self.assertEqual(current_user_votes, {"Drinks": "Tea", "Food": "Coffee"})


if __name__ == "__main__":
    unittest.main()
