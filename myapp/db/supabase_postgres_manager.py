from postgrest import APIError
from supabase import create_client, Client
from myapp.db.manager_exception import ManagerException
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
    
    def add_category(self, category: Category, user_id: int):
        supabase: Client = create_client(
            self.url,
            self.key
        )
        try:
            response = supabase.table('categories').insert({"name": category.name, "user_id": user_id}).execute()
        except APIError as e:
            raise ManagerException("Failed to add category")
        if (response.status_code != 201):
            raise ManagerException("Failed to add category")
        


    