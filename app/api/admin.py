import uuid
from fastapi import APIRouter, Request, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from dependencies.dep_auth import get_current_user
from users.models import User
from core import db_helper as db
from core.config import settings

from crud.achievements import read_sections
from crud.sections import create_instance, update_content, add_img, update_image
from sections.schemas import AchievementCardUpdate, AchievementCardCreate, SectioTitleUpdate, ImageUpdate
from sections.models import models_map


# Инициализация Jinja2Templates с указанием директории шаблонов
admin = Jinja2Templates(directory=settings.files.admin_templates)


router = APIRouter(prefix="/admin", tags=["admin"])


# Чтение всех секций
@router.get("/", response_class=HTMLResponse)
async def get_admin(
    request: Request,
    user: User = Depends(get_current_user),
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
            session=session,
        )
        sections.update({"section": section})
        logger.info(f"Получены данные секции {entity}: {section}")
    
    return admin.TemplateResponse("index.html", sections,)
    
    
# Добавить новую запись
@router.post("/sections/{entity_name}")
async def new_istance(
    entity_name: str,
    payload: AchievementCardCreate,
    session: AsyncSession = Depends(db.get_session_without_commit)
): 
    return await create_instance(
        entity_name=entity_name,
        payload=payload, 
        session=session
    )
    

# ресурс на изменение секции: заголовок, подзаголовок, кнопка
@router.patch("/sections/{id}")
async def patch_section(
    id: int,
    payload: SectioTitleUpdate,
    session: AsyncSession = Depends(db.get_session_with_commit)
):
    return await update_content(
        id=id,
        payload=payload,
        session=session,
    )
    

# ресурс на изменение карточек в секции id=achievemtns
@router.patch("/achievements/{id}")
async def update_achievement(
    id: int,
    payload: AchievementCardUpdate,
    session: AsyncSession = Depends(db.get_session_with_commit)
):
    return await update_content(
        id=id,
        payload=payload,
        session=session
    )


# ресурс на добавление картинки
@router.post("/images/")
async def upload_image(
    image: UploadFile = File(...),
    image_type: str = File(...),
    entity_name: str = File(...),
    entity_id: int = File(...),
    session: AsyncSession = Depends(db.get_session_without_commit),
):
    return await add_img(
        image=image,
        image_type=image_type,
        entity_name=entity_name,
        entity_id=entity_id,
        session=session,
    )


# ресурс на удаление/замену картинки
@router.patch("/images/{entity_name}/{entity_id}")
async def action_img(
    entity_id: int,
    entity_name: str,
    payload: ImageUpdate,
    session: AsyncSession = Depends(db.get_session_without_commit)
):
    return await update_image(
        entity_id=entity_id,
        entity_name=entity_name,
        payload=payload, 
        session=session
    )