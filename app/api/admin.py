from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from core import db_helper as db
from core.config import settings

from crud.achievements import read_achievements, update_achievement
from sections.models import Achievement
from sections.schemas import AchievementUpdate


# Инициализация Jinja2Templates с указанием директории шаблонов
admin = Jinja2Templates(directory=settings.files.admin_templates)


router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/", response_class=HTMLResponse)
async def get_admin(
    request: Request,
    session: AsyncSession = Depends(db.get_session_without_commit)
):
    section_achievements = await read_achievements(session=session, section_id=1)
    # logger.info(f"Получены данные секции archievements: {section_achievements}")
    return admin.TemplateResponse(
        "index.html",  # Имя шаблона
        {
            "request": request,
            "section_achievements": section_achievements,
        }  # Контекст с передачей request
    )
    

@router.patch("/achievements/{id}")
async def patch_achievement(
    id: int,
    update_data: AchievementUpdate,
    session: AsyncSession = Depends(db.get_session_with_commit)
):
    achievement = await update_achievement(id=int(id), update_data=update_data, session=session)
    return achievement

