from postgrest import APIError
import storage3
from supabase import AuthError, create_client, Client
import supabase_auth
from myapp.errors.authentication_error import AuthenticationError
from myapp.errors.db_state_error import DbStateError
from myapp.errors.server_error import ServerError
from myapp.models.category import Category
from myapp.models.thing import Thing
from myapp.user import User
import uuid

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
            categories.append(Category.from_json(item))
        return categories
    
    def add_category(self, category: Category):
        try:
            self.supabase.table('categories').insert({"name": category.name}).execute()
        except APIError as e:
            if self.is_client_error(e.code):
                raise DbStateError("That category already exists", e.code)
            raise ServerError("server error", e.code)
    
    def get_thing(self, name: str):
        try:
            response = self.supabase.table('things').select("*").filter("name", "eq", name).execute()
            if len(response.data) == 0:
                return None
            return Thing.from_json(response.data[0])
        except APIError as e:
            raise ServerError("server error", e.code)
    
    # def update_thing(self, thing: Thing):
    #     try:
    #         if self.get_thing_by_id(thing.from_thing_id) is None:
    #             raise DbStateError("from thing not found", 404)
    #         if self.get_thing(thing.name) is None:
    #             raise DbStateError("thing with that name not found", 404)
    #         if thing.from_thing_name is not None and self.get_thing(thing.from_thing_name) is None:
    #             raise DbStateError("from thing not found", 404)
            
    #         response = self.supabase.table('things').update({
    #             "image_url": thing.image_url, 
    #             "from_thing_name": thing.from_thing_name
    #             }).eq("name", thing.name).execute()
            
    #         return Thing.from_json(response.data[0])
    #     except APIError as e:
    #         raise ServerError("server error", e.code)
        
    # def add_thing(self, thing: Thing):
    #     try:
    #         if self.get_thing(thing.name) is not None:
    #             raise DbStateError("That thing already exists")
    #         if thing.from_thing_name is not None and self.get_thing(thing.from_thing_name) is None:
    #             raise DbStateError("from thing not found", 404)
            
    #         response = self.supabase.table('things').insert({
    #             "name": thing.name, 
    #             "image_url": thing.image_url, 
    #             "from_thing_id": thing.from_thing_id
    #             }).execute()
            
    #         return Thing.from_json(response.data[0])
    #     except APIError as e:
    #         raise ServerError("server error", e.code)
        
    def upsert_thing(self, thing: Thing):
        try:
            if thing.from_thing_name is not None and self.get_thing(thing.from_thing_name) is None:
                raise DbStateError("from thing not found", 404)
            
            response = self.supabase.table('things').upsert({
                "name": thing.name, 
                "img_filename": thing.img_filename, 
                "from_thing_name": thing.from_thing_name
                }).execute()
            
            return Thing.from_json(response.data[0])
        except APIError as e:
            raise ServerError("server error", e.code)
        
    def add_thing_image(self, image_file):
        try:
            new_file_name = f"{image_file.filename}-{uuid.uuid4()}" #to avoid name conflicts in storage
            response = self.supabase.storage.from_('ThingImages').upload(f"{new_file_name}", image_file.read(), 
                                                                         {"content-type": image_file.content_type})
            image_url = self.supabase.storage.from_('ThingImages').get_public_url(f"{new_file_name}")
            return image_url
        except (APIError, storage3.exceptions.StorageApiError) as e:
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
            
            data = response.model_dump()
            return User.from_supabase_row_json(data['user'])
        except AuthError as e:
            raise AuthenticationError("email or name already in use", e.code)
        except APIError as e:
            raise ServerError("server error", e.code)
        
    def login(self, email, password):
        try:
            response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            data = response.model_dump()
            return User.from_supabase_row_json(data['user'])
        except AuthError as e:
            raise AuthenticationError("Invalid email or password", e.code)
        except APIError as e:
            raise ServerError("server error", e.code)
    
    def get_user(self):
        try:
            response = self.supabase.auth.get_user()
            if response is None or response.user is None:
                return None
            
            data = response.model_dump()
            return User.from_supabase_row_json(data['user'])
        except APIError as e:
            raise ServerError("server error", e.code)

        


    