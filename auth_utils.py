"""
Authentication Utilities Module
Provides secure password hashing, JWT token management, and role-based access control.
"""
import bcrypt
import jwt
import os
import json
import re
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple

# ── Configuration ─────────────────────────────────────────────────────────────
JWT_SECRET_KEY = os.environ.get("VULNSAGE_JWT_SECRET", "vulnsage-default-secret-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# ── Password Hashing (bcrypt) ─────────────────────────────────────────────────
def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against a bcrypt hash."""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False


def check_password_strength(password: str) -> Tuple[bool, str]:
    """
    Check password strength requirements.
    Returns (is_valid, message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."
    
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter."
    
    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit."
    
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character."
    
    return True, "Password is strong."


# ── JWT Token Management ─────────────────────────────────────────────────────
def create_jwt_token(user_data: Dict[str, Any]) -> str:
    """
    Create a JWT token for the authenticated user.
    Includes user info, role, and expiration time.
    """
    expiration = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    
    payload = {
        "sub": user_data.get("username", ""),
        "name": user_data.get("name", ""),
        "role": user_data.get("role", "user"),
        "exp": expiration,
        "iat": datetime.utcnow(),
        "type": "access"
    }
    
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token


def verify_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify and decode a JWT token.
    Returns the payload if valid, None otherwise.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        # Token has expired
        return None
    except jwt.InvalidTokenError:
        # Invalid token
        return None


def refresh_jwt_token(token: str) -> Optional[str]:
    """
    Refresh an existing JWT token.
    Returns a new token if the old one is valid.
    """
    payload = verify_jwt_token(token)
    if payload:
        # Create new token with same user data but new expiration
        user_data = {
            "username": payload.get("sub", ""),
            "name": payload.get("name", ""),
            "role": payload.get("role", "user")
        }
        return create_jwt_token(user_data)
    return None


# ── Role-Based Access Control ───────────────────────────────────────────────
class Role:
    """Role constants for RBAC."""
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"


def require_role(required_role: str):
    """
    Decorator/function to check if user has required role.
    Returns True if user has the required role or higher.
    """
    role_hierarchy = {
        Role.ADMIN: 3,
        Role.USER: 2,
        Role.GUEST: 1
    }
    
    def check_role(user_role: str) -> bool:
        user_level = role_hierarchy.get(user_role, 0)
        required_level = role_hierarchy.get(required_role, 0)
        return user_level >= required_level
    
    return check_role


def is_admin(user_role: str) -> bool:
    """Check if user has admin role."""
    return user_role == Role.ADMIN


def is_user(user_role: str) -> bool:
    """Check if user has user role or higher."""
    return user_role in [Role.ADMIN, Role.USER]


# ── User Storage with bcrypt ─────────────────────────────────────────────────
def migrate_users_to_bcrypt(users_dict: Dict) -> Dict:
    """
    Migrate existing MD5-hashed users to bcrypt.
    Only migrates if the password doesn't look like a bcrypt hash.
    """
    migrated = {}
    for username, user_data in users_dict.items():
        password_hash = user_data.get("password", "")
        
        # Check if already bcrypt (starts with $2a$, $2b$, or $2y$)
        if password_hash.startswith(('$2a$', '$2b$', '$2y$')):
            migrated[username] = user_data
        else:
            # This is an old MD5 hash - we need to set a default password
            # In production, you would notify users to reset their passwords
            # For now, we'll keep them but mark them as needing migration
            user_data["needs_password_reset"] = True
            # Default password hint - user must reset
            user_data["password"] = hash_password(f"{username}_temp_2024")
            migrated[username] = user_data
    
    return migrated


# ── Token Storage (for session management) ──────────────────────────────────
def save_token_to_storage(token: str, user_data: Dict) -> bool:
    """Save token to a simple file-based storage."""
    try:
        tokens = load_tokens()
        tokens[token] = {
            "user_data": user_data,
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(hours=JWT_EXPIRATION_HOURS)).isoformat()
        }
        with open("tokens.json", "w") as f:
            json.dump(tokens, f, indent=2)
        return True
    except Exception:
        return False


def load_tokens() -> Dict:
    """Load tokens from storage."""
    try:
        if os.path.exists("tokens.json"):
            with open("tokens.json", "r") as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def remove_token(token: str) -> bool:
    """Remove a token from storage (logout)."""
    try:
        tokens = load_tokens()
        if token in tokens:
            del tokens[token]
            with open("tokens.json", "w") as f:
                json.dump(tokens, f, indent=2)
        return True
    except Exception:
        return False


def cleanup_expired_tokens() -> int:
    """Remove expired tokens from storage. Returns count of removed tokens."""
    try:
        tokens = load_tokens()
        now = datetime.now()
        expired = []
        
        for token, data in tokens.items():
            expires_at = data.get("expires_at", "")
            if expires_at:
                try:
                    exp_time = datetime.fromisoformat(expires_at)
                    if exp_time < now:
                        expired.append(token)
                except Exception:
                    expired.append(token)
        
        for token in expired:
            del tokens[token]
        
        if expired:
            with open("tokens.json", "w") as f:
                json.dump(tokens, f, indent=2)
        
        return len(expired)
    except Exception:
        return 0
