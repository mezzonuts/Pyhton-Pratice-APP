from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from datetime import timedelta

from backend.app.auth import (
    create_access_token,
    decode_token,
    get_current_user,
    get_password_hash,
    oauth_github_callback,
    oauth_github_url,
    verify_password,
)
from backend.app.database import AsyncSessionLocal
from backend.app.models.user import User
from backend.app.schemas.user import UserCreate, UserLogin, UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(payload: UserCreate, response: Response):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.email == payload.email))
        existing = result.scalar_one_or_none()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
        result = await session.execute(select(User).where(User.username == payload.username))
        existing = result.scalar_one_or_none()
        if existing:
            raise HTTPException(status_code=400, detail="Username already taken")
        user = User(
            email=payload.email,
            username=payload.username,
            password_hash=get_password_hash(payload.password),
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_access_token(
            data={"sub": str(user.id)}, expires_delta=timedelta(days=7)
        )
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
        response.set_cookie(
            key="refresh_token",
            value=f"Bearer {refresh_token}",
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        )
        return UserRead.model_validate(user)


@router.post("/login", response_model=UserRead, status_code=status.HTTP_200_OK)
async def login(payload: UserLogin, response: Response):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.email == payload.email))
        user = result.scalar_one_or_none()
        if not user or not verify_password(payload.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Incorrect email or password")
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_access_token(
            data={"sub": str(user.id)}, expires_delta=timedelta(days=7)
        )
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
        response.set_cookie(
            key="refresh_token",
            value=f"Bearer {refresh_token}",
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        )
        return UserRead.model_validate(user)


@router.get("/github", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
async def github_login():
    url = await oauth_github_url()
    return Response(status_code=302, headers={"Location": url})


@router.get("/github/callback", response_model=UserRead, status_code=status.HTTP_200_OK)
async def github_callback(request: Request, response: Response):
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code")
    result = await oauth_github_callback(code, request)
    userinfo = result["userinfo"]
    async with AsyncSessionLocal() as session:
        stmt = select(User).where(User.email == userinfo.email)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            user = User(
                email=userinfo.email,
                username=userinfo.username or userinfo.email.split("@")[0],
                password_hash="",
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_access_token(
            data={"sub": str(user.id)}, expires_delta=timedelta(days=7)
        )
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
        response.set_cookie(
            key="refresh_token",
            value=f"Bearer {refresh_token}",
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        )
        return UserRead.model_validate(user)


@router.get("/me", response_model=UserRead, status_code=status.HTTP_200_OK)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserRead.model_validate(current_user)