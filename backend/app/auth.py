from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

import httpx

from app.database import AsyncSessionLocal
from app.models.user import User
from app.schemas.user import UserRead

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    payload = decode_token(token)
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        if not user.is_active:
            raise HTTPException(status_code=403, detail="Inactive user")
        return user


async def oauth_github_url() -> str:
    # Generate GitHub OAuth URL for @authjs/react
    return "https://github.com/login/oauth/authorize?client_id=your-github-client-id&scope=read:user user:email&redirect_uri=http%3A%2F%2Flocalhost%3A8000%2Fauth%2Fgithub%2Fcallback"


async def oauth_github_callback(code: str, request: Request) -> dict:
    async with httpx.AsyncClient() as client:
        # Exchange code for token
        token_res = await client.post(
            "https://github.com/login/oauth/access_token",
            data={
                "client_id": "your-github-client-id",
                "client_secret": "your-github-client-secret",
                "code": code,
                "redirect_uri": "http://localhost:8000/auth/github/callback",
            },
            headers={"Accept": "application/json"},
        )
        
        if token_res.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get GitHub access token")
        
        # Parse token response (may be query string or JSON)
        token_text = token_res.text
        access_token = None
        if "access_token=" in token_text:
            params = token_text.split("&")
            for param in params:
                if param.startswith("access_token="):
                    access_token = param.split("=", 1)[1]
        elif "access_token" in token_text.json():
            access_token = token_res.json().get("access_token")
        
        # Get user info
        user_res = await client.get(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {access_token}", "Accept": "application/json"},
        )
        
        user_data = user_res.json()
    
    return {"tokens": {"access_token": access_token}, "userinfo": {"email": user_data.get("email"), "username": user_data.get("login")}}