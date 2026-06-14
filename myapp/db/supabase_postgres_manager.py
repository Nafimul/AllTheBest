from supabase import create_client, Client
from myapp.models.category import Category

class SupabasePostgresManager:
    def __init__(self, url, key):
        self.url = url
        self.key = key

    def get_categories(self):
        supabase: Client = create_client(
            self.url,
            self.key
        )
        response = supabase.table('categories').select("*").execute()
        categories = []
        for item in response.data:
            category = Category(
                id=item['id'],
                created_at=item['created_at'],
                name=item['name']
            )
            categories.append(category)
        return categories

    