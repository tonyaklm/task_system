from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, DBAPIError, DataError
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse

from database import get_session
from schemas import user_schemas
from utils.password import encrypt_password, check_encrypted_password
from tables.user_dao import UserDao

router = APIRouter(prefix="/user", tags=["user"])


@router.post("", status_code=201, summary="Register a new user", response_model=user_schemas.Token)
async def registration(user_to_post: user_schemas.UserRegistration,
                       session: AsyncSession = Depends(get_session)):
    """ Registers user by login, password, name and surname. Returns token of a session"""

    user_to_post.password = encrypt_password(user_to_post.password)
    new_user: UserDao = UserDao(first_name=user_to_post.first_name,
                                second_name=user_to_post.second_name,
                                login=user_to_post.login,
                                password=user_to_post.password)
    session.add(new_user)
    try:
        await session.commit()
    except IntegrityError:
        return JSONResponse(status_code=409, content=f"User with login {user_to_post.login} already exist")
    except DBAPIError or DataError:
        return JSONResponse(status_code=400, content="Incorrect data")

    return user_schemas.Token(access_token=new_user.get_token())


@router.post("/authentication", status_code=200, summary="Authenticate a user", response_model=user_schemas.Token)
async def authentication(authentication_data: user_schemas.UserAuthentication,
                         session: AsyncSession = Depends(get_session)):
    """ Authenticates user and returns token of a session"""

    user: UserDao = (
        await session.execute(
            select(UserDao).where(UserDao.login == authentication_data.login))).unique().scalars().one_or_none()
    if not user:
        return JSONResponse(status_code=404, content=f"User {authentication_data.login} does not exist")
    if not check_encrypted_password(authentication_data.password, user.password):
        return JSONResponse(status_code=400, content="Incorrect password")
    return user_schemas.Token(access_token=user.get_token())
