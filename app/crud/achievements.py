from typing import List, TypeVar, Generic, Type
from pydantic import BaseModel
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from sqlalchemy import update as sqlalchemy_update, delete as sqlalchemy_delete, func
from fastapi import HTTPException, Request, Depends
from loguru import logger
from starlette import status


from core.base import Base

from sections.models import Section, Achievement


async def read_achievements(session, section_id):
    query = select(Section).where(Section.id == section_id).options(selectinload(Section.achievements))
    result = await session.execute(query)
    achievement = result.scalars().first()
    return achievement


async def update_achievement(id, update_data, session):
    # Получаем объект из базы
    achievement = await session.get(Achievement, id)
    if not achievement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Achievement {id} не найден"
        )
    # Обновляем только переданные поля
    update_data_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_data_dict.items():
        setattr(achievement, key, value)
    try:
        await session.commit()
        await session.refresh(achievement)
        logger.info(f"Успешное обновление achievement: {achievement}")
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    return achievement