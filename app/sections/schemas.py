from typing import Union
from pydantic import BaseModel, Field


# section
# Валидация для основных заголовков и подзаголовков секций
class EntityUpdate(BaseModel):
    id: int = Field(description="id сущности - обязательное поле")
    table_name: str = Field(description="название таблицы - обязательное поле")
    title: str | None = None
    subtitle: str | None = None
    visibility: str | None = None
    image_desktop: str | None = None
    image_mobile: str | None = None
    image_alt: str | None = None
    button_text: str | None = None
    button_url: str | None = None
    link_text: str | None = None
    link_url: str | None = None
    order_value: int | None = None


# Валидация для изменения карточек
class CardUpdate(BaseModel):
    id: int = Field(description="id карточки - обязательное поле")
    table_name: str = Field(description="название таблицы - обязательное поле")
    title: str | None = None
    description: str | None = None
    image_desktop: str | None = None
    image_mobile: str | None = None
    image_alt: str | None = None
    button_text: str | None = None
    button_url: str | None = None
    link_text: str | None = None
    link_url: str | None = None
    order_value: int | None = None
    
    
class CardCreate(BaseModel):
    section_id: int = Field(description="id секции - обязательное поле")
    table_name: str = Field(description="название таблицы - обязательное поле")
    title: str | None = None
    description: str | None = None
    image_desktop: str | None = None
    image_mobile: str | None = None
    image_alt: str | None = None
    button_text: str | None = None
    button_url: str | None = None
    link_text: str | None = None
    link_url: str | None = None
    order_value: int | None = None
    
    
class EntityDelete(BaseModel):
    id: int = Field(description="id записи - обязательное поле")
    table_name: str = Field(description="название таблицы - обязательное поле")
    
    
# Добавление картинки
class ImageSave(BaseModel):
    id: int = Field(description="id таблицы, к объекту которой относится картинка")
    table_name: str = Field(description="Название таблицы, к объекту которой относится картинка")
    image_name: str | None = Field(default=None, description="название используется для атрибута alt тега img")
    
    
# Удаления/Заменика картинки
class ImageUpdate(BaseModel):
    id: int = Field(description="id таблицы, к объекту которой относится картинка")
    table_name: str = Field(description="Название таблицы, к объекту которой относится картинка")
    image_type: str = Field(description="тип картики. Ожидается image_desktop, или image_mobile")
    image_action: str = Field(description="тип действия над картикой. Ожидается image_delete, или image_refresh")
    image_src: str = Field(description="ресурс картинки для удаления")