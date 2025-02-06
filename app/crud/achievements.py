from sqlalchemy import select
from sqlalchemy.orm import contains_eager
from sqlalchemy.future import select



from sections.models import Section, Achievement


async def read_achievements(session, section_id):
    query = (
        select(Section)
        .join(Achievement, Section.id == Achievement.section_id)
        # Загружаем achievements
        .options(contains_eager(Section.achievements))
        .where(Section.id == section_id)
        .order_by(Section.id, Achievement.order_value)
    )
    result = await session.execute(query)
    achievements = result.scalars().first()
    return achievements


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