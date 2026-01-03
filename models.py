from flask_login import UserMixin
from db import get_user_by_id, get_user_by_username, update_last_login

class User(UserMixin):
    """User model for Flask-Login"""

    def __init__(self, id, username, email, created_at=None, last_login=None):
        self.id = id
        self.username = username
        self.email = email
        self.created_at = created_at
        self.last_login = last_login

    def get_id(self):
        """Return the user id as a string (required by Flask-Login)"""
        return str(self.id)

    @staticmethod
    def get(user_id):
        """Load a user by ID for Flask-Login"""
        user_data = get_user_by_id(user_id)
        if user_data:
            return User(
                id=user_data['id'],
                username=user_data['username'],
                email=user_data['email'],
                created_at=user_data.get('created_at'),
                last_login=user_data.get('last_login')
            )
        return None

    @staticmethod
    def authenticate(username, password):
        """
        Authenticate a user by username and password
        Returns User object if successful, None otherwise
        """
        from auth import verify_password

        user_data = get_user_by_username(username)
        if not user_data:
            return None

        if verify_password(user_data['password_hash'], password):
            # Update last login timestamp
            update_last_login(user_data['id'])

            return User(
                id=user_data['id'],
                username=user_data['username'],
                email=user_data['email'],
                created_at=user_data.get('created_at'),
                last_login=user_data.get('last_login')
            )

        return None

    def __repr__(self):
        return f'<User {self.username}>'
