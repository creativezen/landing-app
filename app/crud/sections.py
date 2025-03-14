import os
import uuid

from core.config import settings
from fastapi import HTTPException, Request, UploadFile, status
from loguru import logger
from sections.models import Section, models_map
from sections.schemas import (CardCreate, EntityDelete, EntityUpdate,
                              ImageUpdate)
from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager

# Сопоставление названий секций с их идентификаторами
sections_map = {
    "achievements": 1,
    "products": 2,
    "strategies": 3,
}


# Получение данных всех секций
async def get_all(request: Request, session: AsyncSession) -> dict:
    """Чтение всех секций
    Args:
        request (Request): Объект запроса, содержащий информацию о HTTP-запросе.
        session (AsyncSession): Текущая асинхронная сессия для взаимодействия с базой данных.
    Returns:
        dict: Словарь, содержащий данные всех секций.
    """
    # Создание списка словарей, где каждый словарь содержит имя секции и её идентификатор
    sections_list = [
        {"name": section_name, "id": section_id}
        for section_name, section_id in sections_map.items()
    ]
    # Инициализация словаря, который будет содержать данные секций
    sections = {
        "request": request,
    }
    for entity in sections_list:
        # читаем конкретную секцию
        section = await read_section(
            section_id=entity["id"],
            entity_name=entity["name"],
            session=session,
        )
        sections.update({entity["name"]: section})
        logger.info(f"Получены данные секции {entity}: {section}")
    return sections


# Чтение данных конкретной секции
async def read_section(section_id: int, entity_name: str, session: AsyncSession):
    """Чтение данных  таблицы связанной с текущей секцией
    Args:
        section_id (int): DI секции
        entity_name (str): название связанной таблицы
        session (AsyncSession): текущая сессия
    Returns:
        object: все записи найденой таблицы
    """
    logger.info(f"ID запрашиваемой секции: {section_id}")
    # Получение модели данных, соответствующей имени секции
    model = models_map[entity_name]
    # Получение атрибута модели Section, соответствующего имени секции
    relation_entity = getattr(Section, entity_name)
    query = (
        select(Section)  # Выборка из таблицы Section
        .add_columns(Section.id)  # Добавление столбца с идентификатором секции
        .outerjoin(
            model, Section.id == model.section_id
        )  # Внешнее соединение с соответствующей моделью
        .options(contains_eager(relation_entity))  # Загрузка связанных данных
        .where(Section.id == section_id)  # Фильтрация по идентификатору секции
        .order_by(
            Section.id, model.order_value
        )  # Сортировка по идентификатору секции и порядковому значению
    )
    result = await session.execute(query)
    relation_data = result.scalars().first()
    return relation_data


async def create_card(table_name: str, payload: CardCreate, session: AsyncSession):
    """Создание записи
    Args:
        table_name (str): название таблицы
        payload (str): данные для создания записи
        session (AsyncSession): текущая сессия
    Returns:
        object: new_card
    """
    model = models_map[table_name]
    new_card = model(**payload.model_dump())
    # получим текущее максимальное значение order_value
    max_value = await get_order_value(model=model, session=session)
    # обновим у нового экземпляра order_value
    new_card.order_value = max_value + 1
    # добавим новую запись
    session.add(new_card)
    await session.commit()
    await session.refresh(new_card)
    return new_card


async def delete_card(table_name: str, payload: EntityDelete, session: AsyncSession):
    """Удаление записи
    Args:
        table_name (str): название таблицы
        payload (dict): данные для получения таблицы
        session (AsyncSession): текущая сессия
    Returns:
        success: "message"
    """
    model = models_map[table_name]
    try:
        # заберем из записи картинки
        query = select(model.image_desktop, model.image_mobile).where(
            model.id == payload.id
        )
        result = await session.execute(query)
        images_list = result.one_or_none()
        # пробежимся по картинкам и удалим каждую с диска
        for image in images_list:
            logger.info(f"Файл {image} передается на удаление...")
            await delete_image(image)
        # после удаления картинок удалим саму запись
        query = delete(model).where(model.id == payload.id)
        await session.execute(query)
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return {"message": "Экземпляр был успешно удален!"}


async def get_order_value(model, session: AsyncSession) -> int:
    """Получение последнего порядкового номера среди записей
    Args:
        model (model): таблица
        session (_type_): текущая сессия
    Returns:
        int: текущее значение или 0
    """
    max_value = await session.execute(func.max(model.order_value))
    order_value = max_value.scalar()
    return order_value if order_value is not None else 0


async def update_content(id: int, payload: EntityUpdate, session: AsyncSession):
    """Обновляем запись
    Args:
        id (int): ID записи
        payload (dict): новые данные
        session (AsyncSession): текущая сессия
    Returns:
        instance: обновленная запись
    """
    model = models_map[payload.table_name]
    logger.info(f"Обовляем данные модели: {model}")
    # Получаем объект из базы
    card = await session.get(model, id)
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Карточка: {id} не найден..."
        )
    # Обновляем только переданные поля
    payload_dict = payload.model_dump(exclude_unset=True)
    for key, value in payload_dict.items():
        # проверяем значение на его отсутствие
        if isinstance(value, str) and value.strip() == "":
            value = None
        # производим запись данных
        setattr(card, key, value)
    try:
        await session.commit()
        await session.refresh(card)
        logger.info(f"Данные успешно обновлены: {card}")
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return card


async def add_img(
    image: UploadFile,
    image_type: str,
    table_name: str,
    id: int,
    session: AsyncSession,
):
    """Добавляем картинку
    Args:
        image (UploadFile): бинарник картинки
        image_type (str): тип картинки (image_desktop, image_mobile)
        table_name (str): имя таблицы
        id (int): ID записи
        session (AsyncSession): текущая сессия
    Returns:
        success: {"message": ...}
    """
    image_url = await save_image(
        image=image,
        image_type=image_type,
        table_name=table_name,
    )
    try:
        model = models_map[table_name]
        query = update(model).where(model.id == id).values({f"{image_type}": image_url})
        field = await session.execute(query)
        logger.info(f"Обновление поля {image_type} успешно!")
        await session.commit()
    except Exception as e:
        logger.error(f"Ошибка при обновлении {table_name}-{image_type}: {e}")
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return {"message": "Изображение успешно сохранено", image_type: field}


async def save_image(image: UploadFile, image_type: str, table_name: str) -> str:
    """Сохраняем картинку
    Args:
        image (UploadFile): бинарник картинки
        image_type (str): тип картинки ("desktop", "mobile")
        table_name (str): название таблицы/сущности
    Returns:
        str: path
    """
    # Записываем изображение на диск и генерируем ссылку на него
    allowed_types = settings.files.allowed_image_types
    allowed_formats = settings.files.allowed_image_formats
    if image is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Изображение не было передано.",
        )
    # Проверяем формат изображения
    if image.content_type not in allowed_formats:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Недопустимый формат изображения. Разрешены только jpg, png, svg, webp.",
        )
    # Проверяем тип изображения
    if image_type not in allowed_types:
        logger.info(
            "Тип изображения неверный или отсутствует (ожидается 'desktop', или 'mobile')"
        )
        return False
    # Генерация уникального имени и пути файла
    file_extension = image.filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4()}_{image_type}.{file_extension}"

    # Проверяем налиличе директории и создаем ее, если требуется
    directory_path = f"{settings.files.image_files}/{table_name}"
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

    file_location = f"{directory_path}/{unique_filename}"
    logger.info(f"Пукть для сохранения картинки: {file_location}")
    try:
        logger.info(f"Попытка чтения файла: {image.filename}")
        file_content = await image.read()
        logger.info(f"Файл прочитан, размер: {len(file_content)} байт")
        with open(file_location, "wb") as buffer:
            buffer.write(file_content)
    except Exception as e:
        logger.error(f"Ошибка при чтении файла: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Ошибка при чтении файла."
        )
    # Генерация URL для изображения
    image_path = f"/{settings.files.image_files}/{table_name}/{unique_filename}"
    return image_path


async def delete_image(file_location: str):
    """Удаление картинки на диске
    Args:
        file_location (str): расположение файла
    Returns:
        success: "message"
    """
    if file_location == None or file_location == "":
        return
    # получаем абсолютный путь к файлу
    file_location = os.path.join(settings.files.base_dir, file_location.lstrip("/"))
    # logger.info(f"{file_location}")
    try:
        # Проверяем, существует ли файл или директория
        if os.path.exists(file_location):
            # Удаляем файл
            os.remove(file_location)
            logger.info(f"Файл {file_location} успешно удален.")
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Файл {file_location} не существует.",
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ошибка при удалении файла {file_location}: {e}",
        )
    return {"message": "Картинка успешно удалена!"}


async def update_image(
    id: int,
    table_name: str,
    payload: ImageUpdate,
    session: AsyncSession,
):
    """Замена или удаление картинки
    Args:
        id (int): ID записи
        table_name (str): название таблицы
        payload (dict): данные для обновления
        session (AsyncSession): текущая сессия
    Returns:
        success: "message"
    """
    action = payload.image_action
    if action not in settings.files.alloewd_image_actions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Недопустимый тип действия {action}. Ожидается image_delete, или image_refresh",
        )
    model = models_map[table_name]
    try:
        if action == "image_delete":
            # удаляем картинку на диске
            await delete_image(payload.image_src)
            query = (
                update(model).where(model.id == id).values({payload.image_type: None})
            )
            logger.info(f"Удаление в поле {payload.image_type} успешно!")
            await session.execute(query)
            await session.commit()
            return {"message": "Изображение успешно удалено"}
        if action == "image_refresh":
            return
            # TODO: реализовать логику замены картинки на новую
            # uploaded_img = await add_img(
            #     image=image,
            #     image_type=image_type,
            #     table_name=table_name,
            #     id=id,
            #     session=session,
            # )
        #     # логика сохранения новой картинки
        #     entity = await session.get(model, id)
        #     setattr(entity, payload.image_type, payload.image_src)
        #     logger.info(f"Обновление в поле {payload.image_type} успешно!")
    except Exception as e:
        logger.error(f"Ошибка при обновлении картинки: {e}")
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return {"message": "Операция по изменению картинки завершена успешно!"}
