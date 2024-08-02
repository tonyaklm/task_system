import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from fastapi import Header, Depends, status
from fastapi.responses import JSONResponse

from database import get_session
from tables.user_dao import UserDao


async def get_user(token: str = Header(...), session: AsyncSession = Depends(get_session)) -> UserDao:
    """Checks token from Header and returns a valid user"""

    if not token:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="Missing Session key"
        )
    try:
        data = jwt.decode(token, settings.jwt_secret_key, algorithms=settings.algorithm)
    except jwt.DecodeError:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="Invalid Session key"
        )
    user_id = data.get("user_id", None)
    if not user_id:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="Invalid Session key"
        )
    user: UserDao = (
        await session.execute(select(UserDao).where(UserDao.id == user_id))).unique().scalars().one_or_none()
    if not user:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="Invalid Session key"
        )
    return user
