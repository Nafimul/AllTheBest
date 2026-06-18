import flask_login


class User(flask_login.UserMixin):
    def from_supabase_row_json(json):
        user = User()
        user.id = json['id']
        user.email = json['email']
        user.name = json['user_metadata']['name']
        return user
