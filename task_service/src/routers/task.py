from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.exc import DBAPIError, DataError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse

from database import get_session
from tables.user_dao import UserDao
from tables.task_dao import TaskDao
from tables.permission_dao import PermissionDao
from utils.auth import get_user
from schemas import task_schemas

router = APIRouter(prefix="/task", tags=["task"])


@router.post("", status_code=201, summary="Create new task", response_model=task_schemas.TaskId)
async def post_task(task_data: task_schemas.NewTask,
                    user: UserDao = Depends(get_user),
                    session: AsyncSession = Depends(get_session)):
    """ Posts new task with title and content. User automatically has changing rights"""

    new_task = TaskDao(user_id=user.id, title=task_data.title, content=task_data.content)
    session.add(new_task)
    try:
        await session.commit()
    except DBAPIError or DataError or IntegrityError:
        return JSONResponse(status_code=400, content="Incorrect data")

    new_permission = PermissionDao(access_user_id=user.id, task_id=new_task.id, access_mode=2)
    session.add(new_permission)
    try:
        await session.commit()
    except IntegrityError:
        return JSONResponse(status_code=400, content="Incorrect data")
    return task_schemas.TaskId(task_id=new_task.id)


@router.put("", status_code=200, summary="Update a task")
async def update_task(task_data: task_schemas.UpdateTask,
                      user: UserDao = Depends(get_user),
                      session: AsyncSession = Depends(get_session)):
    """ Updates task's content and title by its id. User should has changing rights"""

    task: TaskDao = (
        await session.execute(
            select(TaskDao).where(TaskDao.id == task_data.task_id)
        )).unique().scalars().one_or_none()
    if not task:
        return JSONResponse(status_code=404, content=f"Task with id = {task_data.task_id} not found")

    permission: PermissionDao = (
        await session.execute(
            select(PermissionDao).where(PermissionDao.access_user_id == user.id,
                                        PermissionDao.task_id == task_data.task_id, PermissionDao.access_mode == 2)
        )).unique().scalars().one_or_none()
    if not permission:
        return JSONResponse(status_code=403, content="Resource is forbidden")

    task.title = task_data.new_title
    task.content = task_data.new_content
    try:
        await session.commit()
    except DBAPIError or DataError:
        return JSONResponse(status_code=400, content="Incorrect data")


@router.delete("/{task_id}", status_code=204, summary="Delete a task")
async def delete_task(task_id: int,
                      user: UserDao = Depends(get_user),
                      session: AsyncSession = Depends(get_session)):
    """ Deletes task by its id. Only creator can do this"""

    task: TaskDao = (
        await session.execute(
            select(TaskDao).where(TaskDao.id == task_id)
        )).unique().scalars().one_or_none()
    if not task:
        return JSONResponse(status_code=404, content=f"Task with id = {task_id} not found")
    if user.id != task.user_id:
        return JSONResponse(status_code=403, content="Resource is forbidden")
    await session.delete(task)
    await session.commit()


@router.get("/{task_id}", status_code=200, summary="Get a task", response_model=task_schemas.Task)
async def get_task(task_id: int,
                   user: UserDao = Depends(get_user),
                   session: AsyncSession = Depends(get_session)):
    """ Returns task by its id. User should has viewing or changing rights"""

    task: TaskDao = (
        await session.execute(
            select(TaskDao).where(TaskDao.id == task_id)
        )).unique().scalars().one_or_none()
    if not task:
        return JSONResponse(status_code=404, content=f"Task with id = {task_id} not found")

    permission: PermissionDao = (
        await session.execute(
            select(PermissionDao).where(PermissionDao.access_user_id == user.id,
                                        PermissionDao.task_id == task_id)
        )).unique().scalars().one_or_none()
    if not permission:
        return JSONResponse(status_code=403, content="Resource is forbidden")

    return task
