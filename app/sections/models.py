from typing import List
from sqlalchemy import text, ForeignKey, String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.base import Base


class Section(Base):
    __tablename__ = "sections"

    title: Mapped[str] = mapped_column(String, nullable=True)
    subtitle: Mapped[str] = mapped_column(String, nullable=True)
    achievements: Mapped[List["Achievement"]] = relationship(back_populates="section")
    

class Achievement(Base):
    __tablename__ = "achievements"
    
    title: Mapped[str] = mapped_column(String, nullable=True)
    description: Mapped[str] = mapped_column(String, nullable=True)
    order: Mapped[int] = mapped_column(Integer, nullable=True)
    section_id: Mapped[int] = mapped_column(ForeignKey('sections.id'))
    section: Mapped["Section"] = relationship("Section", back_populates="achievements", lazy="joined")


