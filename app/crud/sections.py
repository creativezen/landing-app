import os
import aiofiles.os as aios
import uuid
from fastapi import HTTPException, status
from loguru import logger
from sqlalchemy import update, func

from sections.models import models_map, Achievement
from core.config import settings


async def create_instance(entity_name, payload, session):
    model = models_map[entity_name]
    new_instance = model(**payload.dict())
    # получим текущее максимальное значение order_value
    max_value = await get_order_value(model=model, session=session)
    # обновим у нового экземпляра order_value
    new_instance.order_value = max_value + 1
    # добавим новую запись
    session.add(new_instance)
    await session.commit()
    await session.refresh(new_instance)
    return new_instance


async def get_order_value(model, session) -> int:
    max_value = await session.execute(
        func.max(model.order_value)
    )
    order_value = max_value.scalar()
    return order_value if order_value is not None else 0


async def update_content(id, payload, session):
    """Обновляем контет записи
    Args:
        id (int): ID записи
        payload (dict): новые данные
        session (AsyncSession): текущая сессия
    Returns:
        entity: обновленная запись
    """
    logger.info(f"Сессия: {session}")
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Сессия не была установлена."
        )
    model = models_map[payload.table]
    logger.info(f"Обовляем данные модели: {model}")
    # Получаем объект из базы
    entity = await session.get(model, id)
    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"entity {id} не найден..."
        )
    # Обновляем только переданные поля
    payload_dict = payload.model_dump(exclude_unset=True)
    for key, value in payload_dict.items():
        # проверяем значение на пустую строку
        if isinstance(value, str) and value.strip() == "":
            value = None
        setattr(entity, key, value)
    try:
        await session.commit()
        await session.refresh(entity)
        logger.info(f"Данные успешно обновлены: {entity}")
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    return entity


async def add_img(image, image_type, entity_name, entity_id, session,):
    """Добавляем картинку
    Args:
        image (UploadFile): бинарник картинки
        image_type (str): тип картинки (image_desktop, image_mobile)
        entity_name (str): имя сущности/таблицы
        entity_id (int): ID записи
        session (AsyncSession): текущая сессия
    Returns:
        success: {"message": ...}
    """
    logger.info(f"Сессия: {session}")
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Сессия не была установлена."
        )
    image_url = await save_image(
        image=image,
        image_type=image_type,
        entity_name=entity_name,
    )
    try:
        model = models_map[entity_name]
        query = (
            update(model)
            .where(model.id == entity_id)
            .values({f"{image_type}": image_url})
        )
        field = await session.execute(query)
        logger.info(f"Обновление поля {image_type} успешно!")
        await session.commit()
    except Exception as e:
        logger.error(f"Ошибка при обновлении {entity_name}-{image_type}: {e}")
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    return {"message": "Изображение успешно сохранено", image_type: field}


async def save_image(image, image_type, entity_name):
    """Сохраняем картинку
    Args:
        image (UploadFile): бинарник картинки
        image_type (str): тип картинки ("desktop", "mobile")
        entity_name (str): название таблицы/сущности
    Returns:
        dict: {"message": ""}
    """
    # Записываем изображение на диск и генерируем ссылку на него
    allowed_types = settings.files.allowed_image_types
    allowed_formats = settings.files.allowed_image_formats
    
    if image is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Изображение не было передано."
        )
    # Проверяем формат изображения
    if image.content_type not in allowed_formats:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Недопустимый формат изображения. Разрешены только jpg, png, svg, webp."
        )
    # Проверяем тип изображения
    if image_type not in allowed_types:
        logger.info("Тип изображения неверный или отсутствует (ожидается 'desktop', или 'mobile')")
        return False
    # Генерация уникального имени и пути файла
    file_extension = image.filename.split('.')[-1]
    unique_filename = f"{uuid.uuid4()}_{image_type}.{file_extension}"
    
    # Проверяем налиличе директории и создаем ее, если требуется
    directory_path = f"{settings.files.image_files}/{entity_name}"
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
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ошибка при чтении файла."
        )
    # Генерация URL для изображения
    image_url = f"/{settings.files.image_files}/{entity_name}/{unique_filename}"
    return image_url


async def delete_image(file_location: str):
    """Удаление картинки на диске
    Args:
        file_location (str): расположение файла
    Returns:
        success: "message"
    """
    file_location = os.path.join(settings.files.base_dir, file_location.lstrip("/"))
    logger.info(f"{file_location}")
    try:
        # Проверяем, существует ли файл
        if os.path.exists(file_location):
            # Удаляем файл
            os.remove(file_location)
            logger.info(f"Файл {file_location} успешно удален.")
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Файл {file_location} не существует."
            )
    except Exception as e:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ошибка при удалении файла {file_location}: {e}"
            )
    return {"message": "Картинка успешно удалена!"}


async def update_image(
    entity_id,
    entity_name,
    payload, 
    session,
):
    action = payload.image_action
    if action not in settings.files.alloewd_image_actions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Недопустимый тип действия {action}. Ожидается image_delete, или image_refresh"
        )
    model = models_map[entity_name]
    try:
        if action == 'image_delete':
            # удаляем картинку на диске
            await delete_image(payload.image_src)
            query = update(model).where(model.id == entity_id).values({payload.image_type: None})
            logger.info(f"Удаление в поле {payload.image_type} успешно!")
            await session.execute(query)
            await session.commit()
            return {"message": "Изображение успешно удалено"}
        if action == 'image_refresh':
            return
            # TODO: реализовать логику замены картинки на нову
            # uploaded_img = await add_img(
            #     image=image,
            #     image_type=image_type,
            #     entity_name=entity_name,
            #     entity_id=entity_id,
            #     session=session,
            # )
        #     # логика сохранения новой картинки
        #     entity = await session.get(model, entity_id)
        #     setattr(entity, payload.image_type, payload.image_src)
        #     logger.info(f"Обновление в поле {payload.image_type} успешно!")
    except Exception as e:
        logger.error(f"Ошибка при обновлении картинки: {e}")
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
