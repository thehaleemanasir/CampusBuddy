from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, user_id, email, role):
        self.id = user_id
        self.email = email
        self.role = role

    @classmethod
    def from_dict(cls, user_data):
        return cls(str(user_data["_id"]), user_data["email"], user_data["role"])