from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from loguru import logger

from core.config import settings

from core import db_helper as db
from api import router as router_api
from api.landing import router as router_landing


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Инициализация...")
    yield
    
    logger.info("Завершение...")
    await db.dispose()


main_app = FastAPI(lifespan=lifespan,)
main_app.include_router(router=router_api,)
main_app.include_router(router=router_landing,)
main_app.mount(
    "/static", 
    StaticFiles(directory=settings.files.static_files),
    name="static"
)


if __name__ == "__main__":
    uvicorn.run(
        "main:main_app",
        host=settings.run.host,
        port=settings.run.port,
        reload=True,
    )