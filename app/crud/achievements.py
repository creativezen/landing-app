from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager
from sqlalchemy.future import select
from loguru import logger



from sections.models import Section, Achievement, models_map


async def read_sections(section_id: int, entity_name: str, session: AsyncSession):
    logger.info(f"ID запрашиваемой секции: {section_id}")
    model = models_map[entity_name]
    relation_entity = getattr(Section, entity_name)
    query = (
        select(Section)
        .join(model, Section.id == model.section_id)
        # Загружаем achievements
        .options(contains_eager(relation_entity))
        .where(Section.id == section_id)
        .order_by(Section.id, model.order_value)
    )
    result = await session.execute(query)
    relation_data = result.scalars().first()
    return relation_data


# async def read_images(session, entity_name):
#     images_query = select(Image).where(Image.entity_name == entity_name)
#     pass

    # if section:
    #     # Группируем изображения по achievement_id
    #     achievement_images = {}
    #     for achievement in section.achievements:
    #         achievement_images[achievement.id] = []

    #     # Загружаем изображения для всех achievements
    #     image_stmt = (
    #         select(Image)
    #         .where(
    #             (Image.entity_name == "achievements") &
    #             (Image.entity_id.in_([a.id for a in section.achievements]))
    #         )
    #     )
    #     image_result = await session.execute(image_stmt)
    #     images = image_result.scalars().all()

    #     # Сопоставляем изображения с achievements
    #     for image in images:
    #         if image.entity_id in achievement_images:
    #             achievement_images[image.entity_id].append(image)

    #     # Присваиваем изображения каждому achievement
    #     for achievement in section.achievements:
    #         achievement.images = achievement_images.get(achievement.id, [])

    #     section.achievements.sort(key=lambda x: x.order_value)  # Сортируем achievements
    #     logger.info(section)

    # return section