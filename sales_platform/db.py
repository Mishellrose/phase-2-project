from __future__ import annotations

from typing import List, Dict

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from sales_platform.logging_config import get_logger

logger = get_logger(__name__)


def create_db_engine(db_url: str) -> Engine:
    return create_engine(db_url)


def create_tables(engine: Engine) -> None:
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                store TEXT,
                product TEXT,
                price REAL,
                quantity INTEGER,
                total_sale REAL
            )
        """))
        conn.commit()


def insert_sales(engine: Engine, records: List[Dict]) -> int:
    with engine.connect() as conn:
        for r in records:
            conn.execute(
                text("""
                    INSERT INTO sales (store, product, price, quantity, total_sale)
                    VALUES (:store, :product, :price, :quantity, :total_sale)
                """),
                {
                    "store": r["store"],
                    "product": r["product"],
                    "price": r["price"],
                    "quantity": r["quantity"],
                    "total_sale": r["total_sale"],
                }
            )
        conn.commit()

    logger.info("DB insert complete: inserted=%s", len(records))
    return len(records)


def fetch_sales_by_store(engine: Engine, store_name: str) -> List[Dict]:
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT * FROM sales WHERE store = :store"),
            {"store": store_name}
        )

        rows = result.fetchall()

    return [
        {
            "id": row[0],
            "store": row[1],
            "product": row[2],
            "price": row[3],
            "quantity": row[4],
            "total_sale": row[5],
        }
        for row in rows
    ]