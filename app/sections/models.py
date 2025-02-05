from typing import List
from sqlalchemy import text, ForeignKey, String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.base import Base


class Section(Base):
    __tablename__ = "sections"

    title: Mapped[str] = mapped_column(String, nullable=True)
    subtitle: Mapped[str] = mapped_column(String, nullable=True)
    achievements: Mapped[List["Achievement"]] = relationship(back_populates="section")
    
    
class Card(Base):
    __abstract__ = True
    
    title: Mapped[str] = mapped_column(String, nullable=True)
    description: Mapped[str] = mapped_column(String, nullable=True)
    image_desktop: Mapped[str] = mapped_column(String, nullable=True)
    image_mobile: Mapped[str] = mapped_column(String, nullable=True)
    image_alt: Mapped[str] = mapped_column(String, nullable=True)
    button_text: Mapped[str] = mapped_column(String, nullable=True)
    button_url: Mapped[str] = mapped_column(String, nullable=True)
    order_value: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    

class Achievement(Card):
    __tablename__ = "achievements"
    
    table_name: Mapped[str] = mapped_column(String, nullable=True, server_default="achievements")
    section_id: Mapped[int] = mapped_column(ForeignKey('sections.id'))
    section: Mapped["Section"] = relationship("Section", back_populates="achievements", lazy="joined")
    
    
class Image(Base):
    __tablename__ = 'images'

    image_name: Mapped[str] = mapped_column(String, nullable=True)
    image_url: Mapped[str] = mapped_column(String, nullable=False, default="")
    entity_name: Mapped[str] = mapped_column(String, nullable=False)
    entity_id: Mapped[int] = mapped_column(Integer, nullable=False)
    
    
models_map = {
    'sections': Section,
    'achievements': Achievement,
}


