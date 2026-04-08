from __future__ import annotations

from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Sale(Base):
    __tablename__ = "sales"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    store: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    product: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    total_sale: Mapped[float] = mapped_column(Float, nullable=False)

