from postgrest import APIError
from supabase import create_client, Client
from myapp.db.manager_exception import ManagerException
from myapp.models.category import Category
from myapp.user import User

class SupabasePostgresManager:
    def __init__(self, url, key):
        self.supabase = create_client(
            url, key
        )

    def get_categories(self):
        try:
            response = self.supabase.table('categories').select("*").execute()
        except APIError:
            raise ManagerException("Failed to fetch categories")
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
        try:
            response = self.supabase.table('categories').insert({"name": category.name, "user_id": user_id}).execute()
        except APIError as e:
            raise ManagerException("Failed to add category")
        if (response.status_code != 201):
            raise ManagerException("Failed to add category")
    
    def login(self, email, password):
        response = self.supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        data = response.model_dump()
        user = User()
        user.id = data['user']['id']
        user.email = data['user']['email']
        
        try:
            response = self.supabase.table('profiles').select("*").filter("user_id", "eq", data['user']['id']).execute()
        except APIError:
            raise ManagerException("Failed to fetch user data")
        user.name = response.data[0]['name']

        return user
    
    def get_user(self):
        try:
            response = self.supabase.auth.get_user()
        except APIError:
            raise ManagerException("Failed to fetch user")
        data = response.model_dump()
        user = User()
        user.id = data['user']['id']
        user.email = data['user']['email']

        try:
            response = self.supabase.table('profiles').select("*").filter("user_id", "eq", data['user']['id']).execute()
        except APIError:
            raise ManagerException("Failed to fetch user data")
        user.name = response.data[0]['name']

        return user
        


    