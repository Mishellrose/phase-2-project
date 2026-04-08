from __future__ import annotations

from typing import Iterable, List, Optional

from sqlalchemy import create_engine, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from sales_platform.logging_config import get_logger
from sales_platform.models import Base, Sale

logger = get_logger(__name__)


def create_db_engine(db_url: str) -> Engine:
    return create_engine(db_url, future=True)


def create_tables(engine: Engine) -> None:
    Base.metadata.create_all(engine)


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def insert_sales(session: Session, sales: Iterable[Sale]) -> int:
    sales_list = list(sales)
    session.add_all(sales_list)
    session.commit()
    logger.info("DB insert complete: inserted=%s", len(sales_list))
    return len(sales_list)


def fetch_sales_by_store(session: Session, store_name: str) -> List[Sale]:
    stmt = select(Sale).where(Sale.store == store_name)
    return list(session.scalars(stmt).all())


def to_sale_models(valid_records: list[dict], *, strict: bool = True) -> list[Sale]:
    models: list[Sale] = []
    for r in valid_records:
        store = r.get("store")
        product = r.get("product")
        price = r.get("price")
        qty = r.get("qty")
        total_sale = r.get("total_sale")

        if strict and (store is None or product is None):
            raise ValueError(f"Valid record missing store/product: {r!r}")

        models.append(
            Sale(
                store=str(store),
                product=str(product),
                price=float(price),
                quantity=int(qty),
                total_sale=float(total_sale),
            )
        )
    return models

