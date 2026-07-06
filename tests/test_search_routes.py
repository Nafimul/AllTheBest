import unittest
from unittest.mock import patch

from myapp import create_app
from myapp.models.category import Category
from myapp.models.thing import Thing


class SearchRouteTests(unittest.TestCase):
    def test_search_api_returns_matching_suggestions_for_things_and_categories(self):
        with patch("myapp.create_client", return_value=object()), patch(
            "myapp.SupabaseThingManager.search_things_by_name",
            return_value=[Thing(name="Batman", img_path="")],
        ), patch(
            "myapp.SupabaseCategoryManager.search_categories_by_name",
            return_value=[Category(name="Comics")],
        ):
            app = create_app("testing")
            app.config["TESTING"] = True
            client = app.test_client()

            thing_response = client.get(
                "/api/search",
                query_string={"type": "thing", "q": "bat"},
            )
            self.assertEqual(thing_response.status_code, 200)
            self.assertEqual(thing_response.get_json()[0]["name"], "Batman")

            category_response = client.get(
                "/api/search",
                query_string={"type": "category", "q": "com"},
            )
            self.assertEqual(category_response.status_code, 200)
            self.assertEqual(category_response.get_json()[0]["name"], "Comics")


if __name__ == "__main__":
    unittest.main()
