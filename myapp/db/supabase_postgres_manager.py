from postgrest import APIError
from supabase import create_client, Client
from myapp.errors.auth_error import AuthError
from myapp.errors.db_state_error import DbStateError
from myapp.errors.server_error import ServerError
from myapp.models.category import Category
from myapp.user import User

class SupabasePostgresManager:
    def __init__(self, url, key):
        self.supabase = create_client(
            url, key
        )

    def is_client_error(self, error : str):
            last_three = error[-3:]
            code_int = int(last_three)
            return 400 <= code_int <= 499

    def get_categories(self):
        try:
            response = self.supabase.table('categories').select("*").execute()
        except APIError as e:
            raise ServerError("server error", e.code)
        categories = []
        for item in response.data:
            category = Category(
                id=item['id'],
                created_at=item['created_at'],
                name=item['name']
            )
            categories.append(category)
        return categories
    
    def add_category(self, category: Category):
        try:
            self.supabase.table('categories').insert({"name": category.name}).execute()
            return True
        except APIError as e:
            print("code aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa:" + e.code)
            if self.is_client_error(e.code):
                raise DbStateError("That category already exists", e.code)
            raise ServerError("server error", e.code)
    
    def signup(self, email, password, name):
        try:
            self.supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "name": name
                    }
                }
            })
            return True
        except APIError as e:
            if self.is_client_error(e.code):
                raise DbStateError("email or name already in use", e.code)
            raise ServerError("server error", e.code)
        
    def login(self, email, password):
        try:
            response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            data = response.model_dump()

            user = User()
            user.id = data['user']['id']
            user.email = data['user']['email']
            
            response = self.supabase.table('profiles').select("*").filter("user_id", "eq", data['user']['id']).execute()
            user.name = response.data[0]['name']
            return user
        except APIError as e:
            if self.is_client_error(e.code):
                raise AuthError("Invalid email or password", e.code)
            raise ServerError("server error", e.code)
    
    def get_user(self):
        try:
            response = self.supabase.auth.get_user()
            if response is None or response.user is None:
                return None
            data = response.model_dump()
            
            user = User()
            user.id = data['user']['id']
            user.email = data['user']['email']

            response = self.supabase.table('profiles').select("*").filter("user_id", "eq", data['user']['id']).execute()
            user.name = response.data[0]['name']
            return user
        except APIError as e:
            raise ServerError("server error", e.code)

        


    