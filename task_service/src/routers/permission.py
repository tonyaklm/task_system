from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse

from database import get_session
from schemas import permission_schemas
from tables.permission_dao import PermissionDao
from tables.task_dao import TaskDao
from tables.user_dao import UserDao
from utils.auth import get_user

router = APIRouter(prefix="/permission", tags=["permission"])


@router.post("", status_code=201, summary="Give rights to change/view, 1 - view, 2 - change")
async def post_change_rights(permission_data: permission_schemas.NewRight,
                             user: UserDao = Depends(get_user),
                             session: AsyncSession = Depends(get_session)):
    """ Gives viewing/changing rights to user on specific task"""

    if permission_data.access_mode not in [1, 2]:
        return JSONResponse(status_code=400, content="Access modes : 1 - view, 2 - change")
    task: TaskDao = (
        await session.execute(
            select(TaskDao).where(TaskDao.id == permission_data.task_id)
        )).unique().scalars().one_or_none()
    if not task:
        return JSONResponse(status_code=404, content=f"Task with id = {permission_data.task_id} not found")
    if user.id != task.user_id:
        return JSONResponse(status_code=403, content="Only a creator can provide access")
    access_user: UserDao = (
        await session.execute(
            select(UserDao).where(UserDao.login == permission_data.access_user_login))).unique().scalars().one_or_none()
    if not access_user:
        return JSONResponse(status_code=404, content=f"User {permission_data.access_user_login} does not exist")

    if user.id == access_user.id:
        return JSONResponse(status_code=400, content="Creator can't change his rights")

    permission: PermissionDao = (
        await session.execute(
            select(PermissionDao).where(PermissionDao.access_user_id == access_user.id,
                                        PermissionDao.task_id == permission_data.task_id)
        )).unique().scalars().one_or_none()
    if permission:
        permission.access_mode = permission_data.access_mode
        await session.commit()
        return
    new_permission = PermissionDao(access_user_id=access_user.id,
                                   task_id=permission_data.task_id,
                                   access_mode=permission_data.access_mode)
    session.add(new_permission)
    try:
        await session.commit()
    except IntegrityError:
        return JSONResponse(status_code=400, content="Incorrect data")


@router.delete("/{access_user_login}/{task_id}", status_code=204, summary="Take away rights to change/view a task")
async def delete_rights(access_user_login: str,
                        task_id: int,
                        user: UserDao = Depends(get_user),
                        session: AsyncSession = Depends(get_session)):
    """ Deletes viewing/changing rights"""

    task: TaskDao = (
        await session.execute(
            select(TaskDao).where(TaskDao.id == task_id)
        )).unique().scalars().one_or_none()
    if not task:
        return JSONResponse(status_code=404, content=f"Task with id = {task_id} not found")
    if user.id != task.user_id:
        return JSONResponse(status_code=403, content="Only a creator can take away rights")

    access_user: UserDao = (
        await session.execute(
            select(UserDao).where(UserDao.login == access_user_login))).unique().scalars().one_or_none()
    if not access_user:
        return JSONResponse(status_code=404, content=f"User {access_user_login} does not exist")

    if user.id == access_user.id:
        return JSONResponse(status_code=400, content="Creator can't change his rights")

    permission: PermissionDao = (
        await session.execute(
            select(PermissionDao).where(PermissionDao.access_user_id == access_user.id,
                                        PermissionDao.task_id == task_id)
        )).unique().scalars().one_or_none()
    if not permission:
        return JSONResponse(status_code=404,
                            content=f"Viewing/changing right were not given to {access_user_login}")
    await session.delete(permission)
    await session.commit()
