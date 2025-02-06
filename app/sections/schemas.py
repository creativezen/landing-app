from typing import Union
from pydantic import BaseModel, Field


# section
# Валидация для основных заголовком и подзаголовков секций
class SectioTitleUpdate(BaseModel):
    id: int = Field(description="id секции - обязательное поле")
    table: str = Field(description="название таблицы - обязательное поле")
    title: str | None = None
    subtitle: str | None = None


# id=achievements
# Валидация для изменения карточек
class AchievementCardUpdate(BaseModel):
    id: int = Field(description="id карточки - обязательное поле")
    table: str = Field(description="название таблицы - обязательное поле")
    title: str | None = None
    description: str | None = None
    image_alt: str | None = None
    order: str | None = None
    
    
class AchievementCardCreate(BaseModel):
    section_id: int = Field(description="id секции - обязательное поле")
    table_name: str = Field(description="название таблицы - обязательное поле")
    title: str | None = None
    description: str | None = None
    image_desktop: str | None = None
    image_mobile: str | None = None
    image_alt: str | None = None
    button_text: str | None = None
    button_url: str | None = None
    order_value: int | None = None
    
    
class AchievementCardDelete(BaseModel):
    id: int = Field(description="id записи - обязательное поле")
    table_name: str = Field(description="название таблицы - обязательное поле")
    
    
# Валидция для добавления картинок
class ImageSave(BaseModel):
    # id: int = Field(description="id картинки - обязательное поле")
    entity_id: int = Field(description="id таблицы, к объекту которой относится картинка")
    entity_name: str = Field(description="Название таблицы, к объекту которой относится картинка")
    image_name: str | None = Field(default=None, description="название используется для атрибута alt тега img")
    
    
class ImageUpdate(BaseModel):
    image_type: str = Field(description="тип картики. Ожидается image_desktop, или image_mobile")
    image_action: str = Field(description="тип действия над картикой. Ожидается image_delete, или image_refresh")
    image_src: str = Field(description="ресурс картинки для удаления")
    entity_id: int = Field(description="id таблицы, к объекту которой относится картинка")
    entity_name: str = Field(description="Название таблицы, к объекту которой относится картинка")