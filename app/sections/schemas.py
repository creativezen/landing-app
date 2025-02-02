from pydantic import BaseModel, Field


# Модель Pydantic для входящих данных
class AchievementUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    order: str | None = None
    id: int = Field(description="id секции обязательное поле")