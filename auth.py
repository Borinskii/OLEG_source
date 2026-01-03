from werkzeug.security import generate_password_hash, check_password_hash
import re
from db import create_user, get_user_by_username, get_user_by_email

def hash_password(password: str) -> str:
    """
    Hash a password using werkzeug's secure password hashing
    Uses pbkdf2:sha256 with default iterations
    """
    return generate_password_hash(password, method='pbkdf2:sha256')

def verify_password(password_hash: str, password: str) -> bool:
    """
    Verify a password against its hash
    Returns True if password matches, False otherwise
    """
    return check_password_hash(password_hash, password)

def validate_username(username: str) -> tuple[bool, str]:
    """
    Validate username format
    Returns (is_valid, error_message)
    """
    if not username:
        return False, "Username is required"

    if len(username) < 3:
        return False, "Username must be at least 3 characters long"

    if len(username) > 50:
        return False, "Username must be less than 50 characters"

    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username can only contain letters, numbers, and underscores"

    # Check if username already exists
    if get_user_by_username(username):
        return False, "Username already exists"

    return True, ""

def validate_email(email: str) -> tuple[bool, str]:
    """
    Validate email format
    Returns (is_valid, error_message)
    """
    if not email:
        return False, "Email is required"

    # Basic email regex
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return False, "Invalid email format"

    # Check if email already exists
    if get_user_by_email(email):
        return False, "Email already registered"

    return True, ""

def validate_password(password: str) -> tuple[bool, str]:
    """
    Validate password strength
    Returns (is_valid, error_message)
    """
    if not password:
        return False, "Password is required"

    if len(password) < 6:
        return False, "Password must be at least 6 characters long"

    if len(password) > 100:
        return False, "Password must be less than 100 characters"

    return True, ""

def register_user(username: str, email: str, password: str) -> tuple[bool, str, int]:
    """
    Register a new user
    Returns (success, message, user_id)
    """
    # Validate username
    valid, error = validate_username(username)
    if not valid:
        return False, error, None

    # Validate email
    valid, error = validate_email(email)
    if not valid:
        return False, error, None

    # Validate password
    valid, error = validate_password(password)
    if not valid:
        return False, error, None

    # Hash password
    password_hash = hash_password(password)

    # Create user
    try:
        user_id = create_user(username, email, password_hash)
        return True, "User registered successfully", user_id
    except ValueError as e:
        return False, str(e), None
    except Exception as e:
        return False, f"Error registering user: {e}", None

def login_user_auth(username: str, password: str) -> tuple[bool, str, object]:
    """
    Authenticate user login
    Returns (success, message, user_object)
    """
    from models import User

    if not username or not password:
        return False, "Username and password are required", None

    user = User.authenticate(username, password)

    if user:
        return True, "Login successful", user
    else:
        return False, "Invalid username or password", None
