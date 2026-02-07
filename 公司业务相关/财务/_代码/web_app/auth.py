"""
Authentication module for multi-tenant user management.
Uses JWT tokens and bcrypt password hashing.
"""

from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select
from pydantic import BaseModel, EmailStr

import os
from .database import get_session
from .models import User, Company

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# Password hashing - use pbkdf2_sha256 for better compatibility
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


# Request/Response Models
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    display_name: str = ""
    company_name: str = ""  # Optional: create new company if provided

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    id: int
    email: str
    display_name: str
    company_id: Optional[int]
    company_name: Optional[str]


# Helper Functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


# Dependency: Get current user from token
async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    session: Session = Depends(get_session)
) -> Optional[User]:
    """Returns current user if authenticated, None otherwise."""
    if not token:
        return None
    
    payload = decode_token(token)
    if not payload:
        return None
    
    user_id = payload.get("sub")
    if not user_id:
        return None
    
    user = session.get(User, int(user_id))
    return user


async def require_auth(
    user: Optional[User] = Depends(get_current_user)
) -> User:
    """Requires authentication. Raises 401 if not authenticated."""
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


# Auth Service Functions
def register_user(
    email: str,
    password: str,
    display_name: str,
    company_name: str,
    session: Session
) -> User:
    """Create a new user and optionally a new company."""
    
    # Check if email already exists
    existing = session.exec(select(User).where(User.email == email)).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create company if name provided
    company = None
    if company_name:
        company = Company(name=company_name)
        session.add(company)
        session.flush()  # Get company.id
    
    # Create user
    user = User(
        email=email,
        hashed_password=get_password_hash(password),
        display_name=display_name or email.split("@")[0],
        company_id=company.id if company else None
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    
    return user


def authenticate_user(email: str, password: str, session: Session) -> Optional[User]:
    """Verify credentials and return user if valid."""
    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
