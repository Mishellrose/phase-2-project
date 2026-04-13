from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from typing import List, Dict

from sales_platform.logging_config import get_logger

logger = get_logger(__name__)



def create_db_engine(db_url: str) -> Engine:
    return create_engine(db_url)



def create_tables(engine: Engine) -> None:
    with engine.connect() as conn:

       
        table_exists = conn.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' AND name='sales'")
        ).fetchone()

        if table_exists:
            
            indexes = conn.execute(text("PRAGMA index_list(sales)")).fetchall()

            has_unique = any(row[2] for row in indexes)  # row[2] = is_unique (1 or 0)

            if not has_unique:
                logger.warning("Old table detected without UNIQUE constraint. Recreating table...")
                conn.execute(text("DROP TABLE sales"))

        
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            store TEXT NOT NULL,
            product TEXT NOT NULL,
            price REAL NOT NULL,
            quantity INTEGER NOT NULL,
            total_sale REAL NOT NULL,
            UNIQUE(store, product, price, quantity)
        )
        """))

        conn.commit()


def insert_sales(engine: Engine, records: List[Dict]) -> int:
    query = """
    INSERT INTO sales (store, product, price, quantity, total_sale)
    VALUES (:store, :product, :price, :quantity, :total_sale)
    ON CONFLICT(store, product, price, quantity) DO NOTHING
    """

    with engine.connect() as conn:
        result = conn.execute(text(query), records)
        conn.commit()

    inserted_count = result.rowcount if result.rowcount is not None else 0
    logger.info("Inserted records (deduplicated): %s", inserted_count)

    return inserted_count



def fetch_sales_by_store(engine: Engine, store_name: str) -> List[Dict]:
    query = "SELECT * FROM sales WHERE store = :store"

    with engine.connect() as conn:
        result = conn.execute(text(query), {"store": store_name})
        rows = result.mappings().all()

    return [dict(row) for row in rows]