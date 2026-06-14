from supabase import create_client, Client

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
        return response.data

    
        

    