"""
Authentication and authorization for Vectorpenter
"""

from __future__ import annotations
import secrets
import hashlib
import time
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum
import jwt
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from core.config import settings
from core.logging import logger

class UserRole(str, Enum):
    """User roles for authorization"""
    ADMIN = "admin"
    USER = "user"
    READONLY = "readonly"

@dataclass
class User:
    """User model"""
    username: str
    role: UserRole
    api_key_hash: Optional[str] = None
    created_at: float = 0.0
    last_active: float = 0.0
    
    def __post_init__(self):
        if self.created_at == 0.0:
            self.created_at = time.time()

class APIKeyAuth:
    """Simple API key authentication"""
    
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.api_keys: Dict[str, str] = {}  # api_key -> username
        
    def create_user(self, username: str, role: UserRole = UserRole.USER) -> str:
        """Create a new user and return API key"""
        if username in self.users:
            raise ValueError(f"User {username} already exists")
        
        # Generate secure API key
        api_key = f"vp_{secrets.token_urlsafe(32)}"
        api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        # Create user
        user = User(username=username, role=role, api_key_hash=api_key_hash)
        self.users[username] = user
        self.api_keys[api_key] = username
        
        logger.info(f"Created user: {username} with role: {role}")
        return api_key
    
    def authenticate(self, api_key: str) -> Optional[User]:
        """Authenticate user by API key"""
        if not api_key or api_key not in self.api_keys:
            return None
        
        username = self.api_keys[api_key]
        user = self.users.get(username)
        
        if user:
            user.last_active = time.time()
            
        return user
    
    def require_role(self, required_role: UserRole):
        """Decorator to require specific role"""
        def decorator(func):
            def wrapper(user: User, *args, **kwargs):
                if not self._has_permission(user.role, required_role):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Role {required_role} required"
                    )
                return func(user, *args, **kwargs)
            return wrapper
        return decorator
    
    def _has_permission(self, user_role: UserRole, required_role: UserRole) -> bool:
        """Check if user role has required permissions"""
        role_hierarchy = {
            UserRole.READONLY: 1,
            UserRole.USER: 2,
            UserRole.ADMIN: 3
        }
        
        return role_hierarchy.get(user_role, 0) >= role_hierarchy.get(required_role, 0)

# Global auth instance
auth_manager = APIKeyAuth()

# FastAPI security
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current authenticated user"""
    user = auth_manager.authenticate(credentials.credentials)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return user

async def get_admin_user(user: User = Depends(get_current_user)) -> User:
    """Require admin role"""
    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required"
        )
    return user

async def get_user_or_readonly(user: User = Depends(get_current_user)) -> User:
    """Require user or readonly role"""
    if user.role not in [UserRole.USER, UserRole.ADMIN, UserRole.READONLY]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User role required"
        )
    return user
