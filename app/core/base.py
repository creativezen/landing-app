import uuid
from typing import Annotated
from datetime import datetime
from decimal import Decimal
from sqlalchemy import MetaData, func, TIMESTAMP, Integer, inspect
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from core.config import settings


str_uniq = Annotated[str, mapped_column(unique=True, nullable=False)]


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    metadata = MetaData(
        naming_convention=settings.db.naming_convention,
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.now(), onupdate=func.now()
    )

    def to_dict(self, exclude_none: bool = False):
        """
        Преобразует объект модели в словарь.

        Args:
            exclude_none (bool): Исключать ли None значения из результата

        Returns:
            dict: Словарь с данными объекта
        """
        result = {}
        for column in inspect(self.__class__).columns:
            value = getattr(self, column.key)

            # Преобразование специальных типов данных
            if isinstance(value, datetime):
                value = value.isoformat()
            elif isinstance(value, Decimal):
                value = float(value)
            elif isinstance(value, uuid.UUID):
                value = str(value)
            # Добавляем значение в результат
            if not exclude_none or value is not None:
                result[column.key] = value
        return result
