from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from core import db_helper as db
from core.config import settings
from crud.sections import get_all

# Инициализация Jinja2Templates с указанием директории шаблонов
landing = Jinja2Templates(directory=settings.files.landing_templates)


router = APIRouter(tags=["landing"])


@router.get("/", response_class=HTMLResponse)
async def render_landing(
    request: Request,
    session: AsyncSession = Depends(db.get_session_without_commit)
):  
    # Рендеринг HTML с данными
    return landing.TemplateResponse(
        "index.html", 
        await get_all(request=request, session=session),
    )