from typing import List

from core.base import Base
from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

# Промежуточная таблица для связи многие ко многим
card_badge_achievement = Table(
    "card_badge_achievement",
    Base.metadata,
    Column("card_badge_id", ForeignKey("badges.id"), primary_key=True),
    Column("achievement_id", ForeignKey("achievements.id"), primary_key=True),
)


class Section(Base):
    __tablename__ = "sections"

    title: Mapped[str] = mapped_column(String, nullable=True)
    subtitle: Mapped[str] = mapped_column(String, nullable=True)
    visibility: Mapped[str] = mapped_column(
        String, nullable=True, server_default="visible"
    )
    anchor: Mapped[str] = mapped_column(String, nullable=True)
    # Связь с Achievement
    achievements: Mapped[List["Achievement"]] = relationship(
        "Achievement",
        back_populates="sections",
    )
    # Связь с Product
    products: Mapped[List["Product"]] = relationship(
        "Product", back_populates="sections"
    )
    # Связь со стратегическим видением
    strategies: Mapped[List["Strategy"]] = relationship(
        "Strategy", back_populates="sections"
    )


class CardBadge(Base):
    __tablename__ = "badges"

    value: Mapped[str] = mapped_column(String, nullable=True)
    # Связь с Achievement через промежуточную таблицу
    achievements: Mapped[list["Achievement"]] = relationship(
        "Achievement", secondary=card_badge_achievement, back_populates="badges"
    )


class Card(Base):
    __abstract__ = True

    title: Mapped[str] = mapped_column(String, nullable=True)
    description: Mapped[str] = mapped_column(String, nullable=True)
    image_desktop: Mapped[str] = mapped_column(String, nullable=True)
    image_mobile: Mapped[str] = mapped_column(String, nullable=True)
    image_alt: Mapped[str] = mapped_column(String, nullable=True)
    button_text: Mapped[str] = mapped_column(String, nullable=True)
    button_url: Mapped[str] = mapped_column(String, nullable=True)
    link_text: Mapped[str] = mapped_column(String, nullable=True)
    link_url: Mapped[str] = mapped_column(String, nullable=True)
    order_value: Mapped[int] = mapped_column(Integer, nullable=False, index=True)


class Achievement(Card):
    __tablename__ = "achievements"

    table_name: Mapped[str] = mapped_column(
        String, nullable=True, server_default="achievements"
    )
    section_id: Mapped[int] = mapped_column(ForeignKey("sections.id"))
    sections: Mapped["Section"] = relationship(
        "Section", back_populates="achievements", lazy="joined"
    )
    # Связь с CardBadge через промежуточную таблицу
    badges: Mapped[list["CardBadge"]] = relationship(
        "CardBadge", secondary=card_badge_achievement, back_populates="achievements"
    )


class Product(Card):
    __tablename__ = "products"

    table_name: Mapped[str] = mapped_column(
        String, nullable=True, server_default="products"
    )
    section_id: Mapped[int] = mapped_column(ForeignKey("sections.id"))
    sections: Mapped["Section"] = relationship(
        "Section", back_populates="products", lazy="joined"
    )


class Strategy(Card):
    __tablename__ = "strategies"

    table_name: Mapped[str] = mapped_column(
        String, nullable=True, server_default="strategies"
    )
    section_id: Mapped[int] = mapped_column(ForeignKey("sections.id"))
    sections: Mapped["Section"] = relationship(
        "Section", back_populates="strategies", lazy="joined"
    )


models_map = {
    "sections": Section,
    "achievements": Achievement,
    "products": Product,
    "strategies": Strategy,
}
