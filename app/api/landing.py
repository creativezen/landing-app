from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from core import db_helper as db
from core.config import settings
from crud.achievements import read_sections

# Инициализация Jinja2Templates с указанием директории шаблонов
landing = Jinja2Templates(directory=settings.files.landing_templates)


router = APIRouter(tags=["landing"])


@router.get("/", response_class=HTMLResponse)
async def render_landing(
    request: Request,
    session: AsyncSession = Depends(db.get_session_without_commit)
):
    entities = [
        "achievements",
    ]
    sections = {
        "request": request,
    }
    for entity in entities:
        section = await read_sections(
            section_id=1, 
            entity_name=entity,
            session=session
        )
        sections.update({"section": section})
        logger.info(f"Получены данные секции {entity}: {section}")
    
    # Рендеринг HTML с данными
    return landing.TemplateResponse("index.html", sections)