from contextlib import asynccontextmanager

import uvicorn
from api import router as router_api
from api.admin import router as router_admin
from api.landing import router as router_landing
from core import db_helper as db
from core.config import settings
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from loguru import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Инициализация...")
    yield

    logger.info("Завершение...")
    await db.dispose()


main_app = FastAPI(
    lifespan=lifespan,
)
main_app.include_router(
    router=router_api,
)
main_app.include_router(
    router=router_landing,
)
main_app.include_router(router=router_admin)

main_app.mount(
    "/static", StaticFiles(directory=settings.files.static_files), name="static"
)


if __name__ == "__main__":
    uvicorn.run(
        "main:main_app",
        host=settings.run.host,
        port=settings.run.port,
        reload=True,
    )
