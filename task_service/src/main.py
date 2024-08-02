from fastapi import FastAPI
import uvicorn
from routers import user, task, permission
import asyncio
from database import init_models

app = FastAPI()

app.include_router(user.router)
app.include_router(task.router)
app.include_router(permission.router)

if __name__ == "__main__":
    asyncio.run(init_models())
    uvicorn.run("main:app", host="0.0.0.0", reload=True, port=8000)
