from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager
from sqlalchemy.future import select
from loguru import logger


from sections.models import Section, models_map


async def read_sections(section_id: int, entity_name: str, session: AsyncSession):
    logger.info(f"ID запрашиваемой секции: {section_id}")
    model = models_map[entity_name]
    relation_entity = getattr(Section, entity_name)
    query = (
        select(Section)
        .add_columns(Section.id)
        .outerjoin(model, Section.id == model.section_id)
        .options(contains_eager(relation_entity))
        .where(Section.id == section_id)
        .order_by(Section.id, model.order_value)
    )
    result = await session.execute(query)
    relation_data = result.scalars().first()
    return relation_data

