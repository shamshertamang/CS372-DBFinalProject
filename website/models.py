# models.py

from flask_login import UserMixin
import json

class User(UserMixin):
    def __init__(self, user_row):
        self.id = user_row['id']
        self.user_name = user_row['user_name']
        self.email = user_row['email']
        self.password = user_row['password']
        try:
            # dietary_preferences is stored as JSON string
            self.dietary_preferences = json.loads(user_row['dietary_preferences']) if user_row['dietary_preferences'] else []
        except:
            self.dietary_preferences = []
        self.cooking_level = user_row['cooking_level']
        try:
            self.allergies = json.loads(user_row['allergies']) if user_row['allergies'] else []
        except:
            self.allergies = []
        self.photo_data = user_row['photo_data']

    @property
    def profile_image(self):
        return self.photo_data

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)
