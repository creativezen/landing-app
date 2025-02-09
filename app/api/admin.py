import uuid
from fastapi import (APIRouter, Request, Depends, UploadFile, File,)
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from dependencies.dep_auth import get_current_user
from users.models import User
from core import db_helper as db
from core.config import settings

from crud.sections import get_all, create_card, update_content, add_img, update_image, delete_card
from sections.schemas import (CardCreate, EntityDelete, EntityUpdate, ImageUpdate,)


# Инициализация Jinja2Templates с указанием директории шаблонов
admin = Jinja2Templates(directory=settings.files.admin_templates)


router = APIRouter(prefix="/admin", tags=["admin"])


# Чтение всех секций
@router.get("/", response_class=HTMLResponse)
async def get_admin(
    request: Request,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(db.get_session_without_commit),
):
    return admin.TemplateResponse(
        "index.html",
        await get_all(request=request, session=session),
    )


# Добавить новую запись к вложенной в секцию сущности
@router.post("/sections/{table_name}")
async def new_istance(
    table_name: str,
    payload: CardCreate,
    session: AsyncSession = Depends(db.get_session_without_commit),
):
    return await create_card(
        table_name=table_name, 
        payload=payload,
        session=session
    )
    
    
# Удалить запись из вложенной в секцию сущности
@router.delete("/sections/{table_name}")
async def remove_instance(
    table_name: str,
    payload: EntityDelete,
    session: AsyncSession = Depends(db.get_session_without_commit)
):
    return await delete_card(
        table_name=table_name,
        payload=payload,
        session=session
    )


# ресурс на изменение секции: заголовок, подзаголовок, кнопка
@router.patch("/sections/{id}")
async def patch_section(
    id: int,
    payload: EntityUpdate,
    session: AsyncSession = Depends(db.get_session_with_commit),
):
    return await update_content(
        id=id,
        payload=payload,
        session=session,
    )


# ресурс на изменение карточки
@router.patch("/{table_name}/{id}")
async def patch_card(
    id: int,
    table_name: str,
    payload: EntityUpdate,
    session: AsyncSession = Depends(db.get_session_with_commit),
):
    return await update_content(
        id=id,
        payload=payload,
        session=session
    )


# ресурс на добавление картинки
@router.post("/images/")
async def post_image(
    image: UploadFile = File(...),
    image_type: str = File(...),
    table_name: str = File(...),
    id: int = File(...),
    session: AsyncSession = Depends(db.get_session_without_commit),
):
    return await add_img(
        image=image,
        image_type=image_type,
        table_name=table_name,
        id=id,
        session=session,
    )


# ресурс на удаление/замену картинки
@router.patch("/images/{table_name}/{id}")
async def patch_img(
    id: int,
    table_name: str,
    payload: ImageUpdate,
    session: AsyncSession = Depends(db.get_session_without_commit),
):
    return await update_image(
        id=id,
        table_name=table_name,
        payload=payload,
        session=session
    )
